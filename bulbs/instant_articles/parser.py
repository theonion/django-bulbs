class InstantArticleParser():

    def __init__(self, intermediate):
        pass

    def generate_body(self, intermediate):
        body = ""
        for key, body in intermediate.iteritems():
            body.append(parse_item(key, body))

    def parse_item(self, key, body):
        if key == "text":
            return body
        elif key == "betty":
            return self.parse_betty(body)
        elif key == "facebook":
            return self.parse_facebook(body)
        elif key == "twitter":
            return self.parse_twitter(body)
        elif key == "instagram":
            return self.parse_instagram(body)
        elif key == "onion_video":
            return self.parse_onion_video(body)
        elif key == "vimeo":
            return self.parse_vimeo(body)
        elif key == "youtube":
            return self.parse_youtube(body)
        elif key == "soundcloud":
            return self.parse_soundcloud(body)
        else:
            raise Exception("Key not implemented")

    def parse_betty(self, body):
        pass

    def parse_facebook(self, body):
        pass

    def parse_twitter(self, body):
        pass

    def parse_instagram(self, body):
        pass

    def parse_onion_video(self, body):
        pass

    def parse_vimeo(self, body):
        pass

    def parse_youtube(self, body):
        pass

    def parse_soundcloud(self, body):
        pass
