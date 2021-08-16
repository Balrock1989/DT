class Action:

    def __init__(self, partner_name):
        self.partner_name = partner_name
        self.name = None
        self.end = None
        self.desc = None
        self.start = None
        self.code = None
        self.url = None
        self.action_type = None
        self.short_desc = None

    def __str__(self):
        return self.partner_name

