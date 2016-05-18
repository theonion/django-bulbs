from django.template import loader


class BaseRenderer:

    def generate_body(self, intermediate):
        body = ""
        for item in intermediate:
            for key, values in item.items():
                body += self.render_item(key, values)

        return body

    def render_item(self, key, body):
        if key == "text":
            return body
        elif key == "betty":
            return self.render_betty(body)
        elif key == "facebook":
            return self.render_facebook(body)
        elif key == "imgur":
            return self.render_imgur(body)
        elif key == "instagram":
            return self.render_instagram(body)
        elif key == "onion_video":
            return self.render_onion_video(body)
        elif key == "soundcloud":
            return self.render_soundcloud(body)
        elif key == "twitter":
            return self.render_twitter(body)
        elif key == "vimeo":
            return self.render_vimeo(body)
        elif key == "youtube":
            return self.render_youtube(body)
        else:
            raise Exception("Key not implemented")

    def render_betty(self, body):
        return loader.render_to_string(
            self.BETTY_TEMPLATE,
            body
        )

    def render_facebook(self, body):
        return loader.render_to_string(
            self.FACEBOOK_TEMPLATE,
            body
        )

    def render_imgur(self, body):
        return loader.render_to_string(
            self.IMGUR_TEMPLATE,
            body
        )

    def render_instagram(self, body):
        return loader.render_to_string(
            self.INSTAGRAM_TEMPLATE,
            body
        )

    def render_onion_video(self, body):
        return loader.render_to_string(
            self.ONION_VIDEO_TEMPLATE,
            body
        )

    def render_soundcloud(self, body):
        return loader.render_to_string(
            self.SOUNDCLOUD_TEMPLATE,
            body
        )

    def render_twitter(self, body):
        return loader.render_to_string(
            self.TWITTER_TEMPLATE,
            body
        )

    def render_vimeo(self, body):
        return loader.render_to_string(
            self.VIMEO_TEMPLATE,
            body
        )

    def render_youtube(self, body):
        return loader.render_to_string(
            self.YOUTUBE_TEMPLATE,
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
