from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from socialnetwork.models import Post, Profile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Invalid username/password!')

        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=200,
                                       label='Confirm password',
                                       widget=forms.PasswordInput())
    email = forms.CharField(max_length=50,
                            widget=forms.EmailInput())
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match!')

        return cleaned_data


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('profile', 'date_time')
        widgets = {
            'text': forms.Textarea(attrs={'id': 'id_post_input_text', 'rows': '3'})
        }

    def cleaned_post(self):
        post = self.cleaned_data['profile', 'text', 'date_time']
        if not post:
            raise forms.ValidationError('Post invalid!')
        return post


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'picture')
        widgets = {
            'bio': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': '3'}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture', 'accept': {'image/jpg', 'image/jpeg', 'image/png'}})
        }
        labels = {
            'bio': '',
            'picture': "Upload Image"
        }

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        return picture
