from django import forms
from system.models import Tenant


class TenantSelectForm(forms.Form):
    tenant_id = forms.ModelChoiceField(
        queryset=Tenant.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.Select
    )
    