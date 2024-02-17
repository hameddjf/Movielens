from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Episode, EpisodeQuality  # فرض می‌کنیم که مدل‌های Episode و EpisodeQuality در همین فایل هستند

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_movie_type', 'season', 'view_qualities_link')
    search_fields = ('title',)
    exclude = ('slug',)

    def view_qualities_link(self, obj):
        count = obj.qualities.count()
        url = (
            reverse('admin:appname_episodequality_changelist')  # تغییر appname به نام اپلیکیشن شما
            + '?'
            + 'episode__id__exact={}'.format(obj.id)
        )
        return format_html('<a href="{}">{} کیفیت‌ها</a>', url, count)
    view_qualities_link.short_description = 'کیفیت‌ها'

    def get_movie_type(self, obj):
        return 'سریال' if isinstance(obj.movie, Series) else 'فیلم سینمایی'
    get_movie_type.short_description = 'نوع'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['media'] = self.media + mark_safe('''
            <script type="text/javascript">
                document.addEventListener('DOMContentLoaded', function() {
                    function toggleSeasonInput() {
                        var movieContentTypeId = document.querySelector('input[name="movie_content_type"]').value;
                        var isSeries = movieContentTypeId == "{series_ct_id}";  // جایگزین کردن با ID محتوای نوع Series
                        var seasonInput = document.querySelector("#id_season");
                        if (seasonInput) {
                            seasonInput.closest('.form-row').style.display = isSeries ? 'block' : 'none';
                        }
                    }
                    toggleSeasonInput();
                    var movieContentTypeSelect = document.querySelector('#id_movie_content_type');
                    if (movieContentTypeSelect) {
                        movieContentTypeSelect.addEventListener('change', toggleSeasonInput);
                    }
                });
            </script>
        '''.format(series_ct_id=ContentType.objects.get_for_model(Series).id))
        return super().change_view(request, object_id, form_url, extra_context=extra_context)