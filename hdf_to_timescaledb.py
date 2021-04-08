from datetime import datetime
import time
import h5py
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
import psycopg2

from config_secret import pg

df_header = ["time", "voltage", "current"]
datatypes = {"time": "Time", "node_id": "Integer", "current": "Float", "voltage": "Float"}

def ds_to_phys(dataset: h5py.Dataset):
    gain = dataset.attrs["gain"]
    offset = dataset.attrs["offset"]
    return dataset[:] * gain + offset


def extract_hdf(hdf_file: Path) -> pd.DataFrame:
    with h5py.File(hdf_file, "r") as hf:
        data = dict()
        for var in df_header[1:]:
            sig_phys = ds_to_phys(hf["data"][var])
            data[var] = sig_phys

        time_index = hf["data"]["time"][:]
        data_len = min(
            [len(time_index), len(data["voltage"]), len(data["current"])]
        )
        time_index = time_index[:data_len]
        data["time"] = hf["data"]["time"][:].astype(float) / 1e9
        data["current"] = data["current"][:data_len]
        data["voltage"] = data["voltage"][:data_len]
        df = pd.DataFrame(data=data, columns=df_header, index=time_index)
        df["time"] = df["time"].apply(lambda x: datetime.fromtimestamp(x))
        print("HDF extracted..")
    return df


def put_in_timescale(data: pd.DataFrame, node_id: int):
    engine = create_engine(f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}", )
    data.insert(1, "node_id", node_id)
    batch_size = 1000
    print(f"writing dataframe to database")
    data.to_sql(pg['table'], engine, index=False, chunksize=batch_size, if_exists="replace", method="multi", )
    # todo: adding a scheme can help transparency
    # method="multi"
    # schema="(time, node_id, current, voltage)"  # WRONG
    # dtype=datatypes  # time-datatype is not recognized, https://docs.sqlalchemy.org/en/14/core/type_basics.html#generic-types


if __name__ == "__main__":
    data = extract_hdf(Path("./rec.6.h5"))
    sample_size = 1000000
    data = data.iloc[:sample_size,:]
    print(f"Dataset data: {datetime.fromtimestamp(data.index[0]/1e9)}")
    print(f"Writing Batch of: {data.shape} entries, {data.shape[0]/1e5} sec\n {data.dtypes}")
    print(data.iloc[0:5, :])
    time_start = time.time()
    put_in_timescale(data, 0)
    print(f"Insertion took {round(time.time() - time_start, 2)} seconds")

# results:
# - 16.5 s, 1M Insert, replace, single-insert, batch=2000, -> 40 % cpu, batch-size has no influence
# - 43.5 s, 1M Insert, replace, multi-insert, batch=1000
# - 44.2 s, 1M Insert, replace, multi-insert, batch=2000
# - 46.4 s, 1M Insert, replace, multi-insert, batch=4000
# - ram usage is higher, same with cpu on VM (~60% on one core)

# TODO: pandas also supports directly reading dataframe
# TODO:
# - prepared statements
# - optimize guid
# - binary type i/o
# - try asyncpg?

#connection = psycopg2.connect(user=pg["user"], password=pg["password"],
#                              host=pg["host"], port=pg["port"],
#                              dbname=pg["database"])
#cursor = connection.cursor()
