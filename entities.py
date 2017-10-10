import mongoengine


mongoengine.connect("WSGIdata")

class Link(mongoengine.Document):
    shortcut = mongoengine.StringField()
    link = mongoengine.StringField()


if __name__ == "__main__":
    for link in Link.objects:
        print(link.shortcut, link.link)