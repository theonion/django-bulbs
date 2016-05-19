from django.template import loader


class BaseRenderer:

    def generate_body(self, intermediate):
        body = []
        for item in intermediate:
            for key, values in item.items():
                body.append(self.render_item(key, values).strip())
        return '\n'.join(body)

    def render_item(self, key, body):
        if key == "text":
            return body["raw"]
        elif key == "betty":
            return self.render(self.BETTY_TEMPLATE, body)
        elif key == "facebook":
            return self.render(self.FACEBOOK_TEMPLATE, body)
        elif key == "imgur":
            return self.render(self.IMGUR_TEMPLATE, body)
        elif key == "instagram":
            return self.render(self.INSTAGRAM_TEMPLATE, body)
        elif key == "onion_video":
            return self.render(self.ONION_VIDEO_TEMPLATE, body)
        elif key == "soundcloud":
            return self.render(self.SOUNDCLOUD_TEMPLATE, body)
        elif key == "twitter":
            return self.render(self.TWITTER_TEMPLATE, body)
        elif key == "vimeo":
            return self.render(self.VIMEO_TEMPLATE, body)
        elif key == "youtube":
            return self.render(self.YOUTUBE_TEMPLATE, body)
        else:
            raise Exception("Key not implemented")

    def render(self, template, body):
        return loader.render_to_string(
            template,
            body
        )


class InstantArticleRenderer(BaseRenderer):

    BETTY_TEMPLATE = "instant_article/embeds/_ia_betty_embed.html"
    FACEBOOK_TEMPLATE = "instant_article/embeds/_ia_facebook_embed.html"
    IMGUR_TEMPLATE = "instant_article/embeds/_ia_imgur_embed.html"
    INSTAGRAM_TEMPLATE = "instant_article/embeds/_ia_instagram_embed.html"
    ONION_VIDEO_TEMPLATE = "instant_article/embeds/_ia_onion_video_embed.html"
    SOUNDCLOUD_TEMPLATE = "instant_article/embeds/_ia_soundcloud_embed.html"
    TWITTER_TEMPLATE = "instant_article/embeds/_ia_twitter_embed.html"
    VIMEO_TEMPLATE = "instant_article/embeds/_ia_vimeo_embed.html"
    YOUTUBE_TEMPLATE = "instant_article/embeds/_ia_youtube_embed.html"
