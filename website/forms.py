from django import forms
from .models import Vehicle, VehicleImage, FaultyPart, FaultyPartImage, WheelImage, VehicleDocument

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['car_number', 'brand', 'kilometers', 'cylinder_count', 'mesures', 'ligne']
        widgets = {
            'car_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'brand': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'kilometers': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'cylinder_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'mesures': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'ligne': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none'}),
        }

class FaultyPartForm(forms.ModelForm):
    class Meta:
        model = FaultyPart
        fields = ['part_name', 'description']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 4}),
        }

class FaultyPartImageForm(forms.ModelForm):
    class Meta:
        model = FaultyPartImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none'}),
        }

class WheelImageForm(forms.ModelForm):
    class Meta:
        model = WheelImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none'}),
        }

class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document']
        widgets = {
            'document': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none'}),
        }
