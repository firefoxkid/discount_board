from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        lables = {'text': 'Содержание поста',
                  'group': 'В каком сообществе',
                  'image': 'Можете добавить изображение'
                  }

    def clean_text(self):
        """Валидация! Обрабатывает случай, если текст не уникален."""
        cleaned_data = super().clean()
        post_text = cleaned_data['text']
        if Post.objects.filter(text=post_text).exists():
            self.add_error("text",
                           "Текст не уникален или вы не редактирвали его!")
        return post_text


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        lables = {'text': 'Ваш комментарий'}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 3})
        }
