from django.forms import ModelForm
from .models import Observer


class ObserverForm(ModelForm):
    # TODO: can this have a title and name for send-button?
    class Meta:
        model = Observer
        '''
        fields = ['name',
                  'description',
                  'comment',
                  'ip',
                  'mac',
                  'room',
                  'eth_port',
                  'longitude',
                  'latitude',
                  'target_a_id',

                  ]  # observer.field_names?
        '''
        fields = "__all__"

