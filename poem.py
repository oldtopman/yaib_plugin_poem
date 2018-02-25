"""
Limericks, Tanka, and Haiku

Save and randomly display haiku, tanka, and limericks. Includes some very light
management tools for cleaning up terrible entries or correcting submission
mistakes.
"""

import datetime
import random
import string

from plugins.baseplugin import BasePlugin

from plugins.poem.models import Poem

# TODO: make configurable from settings
RECENT_POEM_LIMIT = 5


class Plugin(BasePlugin):
    """Poems! Haikus and Limericks, oh my!"""

    name = 'PoemPlugin'
    recent_poem_ids = []

    def save_poem(self, poem_type, nick, content):
        with self.getDbSession() as db_session:
            deletion_key = ''.join([
                random.choice(string.letters) for i in range(16)
            ])

            new_poem = Poem(
                submitted_by=nick,
                submitted_time=datetime.datetime.now(),
                poem_type=poem_type,
                content=content,
                deletion_key=deletion_key
            )
            db_session.add(new_poem)

            return deletion_key

    def delete_poem(self, poem_type, deletion_key):
        with self.getDbSession() as db_session:
            query = db_session.query(Poem).filter(
                Poem.deletion_key == deletion_key,
                Poem.poem_type == poem_type
            )

            matching = query.all()

            if len(matching) > 0:
                self.recent_poem_ids.remove(matching[0].id)
                query.delete()
                return True

            return False

    def get_random_poem(self, poem_type='haiku', contains=None, by=None):
        with self.getDbSession() as db_session:
            query = db_session.query(Poem).filter(
                Poem.poem_type == poem_type
            ).order_by(
                Poem.last_served
            )

            if contains is not None:
                query = query.filter(
                    Poem.content.like('%{}%'.format(contains))
                )

            if by is not None:
                query = query.filter(Poem.submitted_by == by)

            poems = query.limit(5).all()

            if len(poems) == 0:
                return 'No matching {} found. Submit one!'.format(poem_type)

            poem = random.choice(poems)

            # update poem
            poem.times_served += 1
            poem.last_served = datetime.datetime.now()
            db_session.add(poem)

            # save in list of recently displayed poems
            if poem.id not in self.recent_poem_ids:
                self.recent_poem_ids.append(poem.id)
                self.recent_poem_ids = (
                    self.recent_poem_ids[-RECENT_POEM_LIMIT:]
                )

            return poem.get_display_message()

    def command_haiku(self, user, nick, channel, rest):
        """Display a random haiku."""

        if rest != '':
            content = rest.strip()
            lines = content.split('/')
            if len(lines) != 3:
                self.reply(
                    channel,
                    nick,
                    'Haiku are 3 lines! Separate lines with /'
                )
                return

            deletion_key = self.save_poem('haiku', nick, content)
            self.reply(channel, nick, 'Haiku Saved!')

            if channel != nick and deletion_key:
                self.send(
                    nick,
                    'You can delete this haiku with /msg {} '
                    'deletehaiku {}'.format(
                        self.nick,
                        deletion_key
                    )
                )
            return

        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='haiku')
        )

    def command_haikuwith(self, user, nick, channel, rest):
        """Display a random haiku with the given text"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='haiku', contains=rest)
        )

    def command_haikuby(self, user, nick, channel, rest):
        """Display a random haiku submitted by the given nick"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='haiku', by=rest)
        )

    def command_deletehaiku(self, user, nick, channel, rest):
        """Delete a haiku using the deletion key."""
        deleted = self.delete_poem('haiku', rest.strip())
        if deleted:
            self.reply(channel, nick, 'Deleted Haiku!')
        else:
            self.reply(
                channel,
                nick,
                'Could not find haiku with that deletion key :('
            )

    def get_random_poem(self, poem_type='tanka', contains=None, by=None):
        with self.getDbSession() as db_session:
            query = db_session.query(Poem).filter(
                Poem.poem_type == poem_type
            ).order_by(
                Poem.last_served
            )

            if contains is not None:
                query = query.filter(
                    Poem.content.like('%{}%'.format(contains))
                )

            if by is not None:
                query = query.filter(Poem.submitted_by == by)

            poems = query.limit(5).all()

            if len(poems) == 0:
                return 'No matching {} found. Submit one!'.format(poem_type)

            poem = random.choice(poems)

            # update poem
            poem.times_served += 1
            poem.last_served = datetime.datetime.now()
            db_session.add(poem)

            # save in list of recently displayed poems
            if poem.id not in self.recent_poem_ids:
                self.recent_poem_ids.append(poem.id)
                self.recent_poem_ids = (
                    self.recent_poem_ids[-RECENT_POEM_LIMIT:]
                )

            return poem.get_display_message()

    def command_tanka(self, user, nick, channel, rest):
        """Display a random tanka."""

        if rest != '':
            content = rest.strip()
            lines = content.split('/')
            if len(lines) != 5:
                self.reply(
                    channel,
                    nick,
                    'Tanka are 5 lines! Separate lines with /'
                )
                return

            deletion_key = self.save_poem('tanka', nick, content)
            self.reply(channel, nick, 'Tanka Saved!')

            if channel != nick and deletion_key:
                self.send(
                    nick,
                    'You can delete this tanka with /msg {} '
                    'deletetanka {}'.format(
                        self.nick,
                        deletion_key
                    )
                )
            return

        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='tanka')
        )

    def command_tankawith(self, user, nick, channel, rest):
        """Display a random tanka with the given text"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='tanka', contains=rest)
        )

    def command_tankaby(self, user, nick, channel, rest):
        """Display a random tanka submitted by the given nick"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='tanka', by=rest)
        )

    def command_deletetanka(self, user, nick, channel, rest):
        """Delete a tanka using the deletion key."""
        deleted = self.delete_poem('tanka', rest.strip())
        if deleted:
            self.reply(channel, nick, 'Deleted Tanka!')
        else:
            self.reply(
                channel,
                nick,
                'Could not find tanka with that deletion key :('
            )

    def command_limerick(self, user, nick, channel, rest):
        """Saves the given limerick or display a random one if no
        additional parameters given.
        """
        if rest != '':
            content = rest.strip()
            lines = content.split('/')
            if len(lines) != 5:
                self.reply(
                    channel,
                    nick,
                    'Limericks are 5 lines! Separate lines with /'
                )
                return

            deletion_key = self.save_poem('limerick', nick, content)
            self.reply(channel, nick, 'Limerick Saved!')

            if channel != nick and deletion_key:
                self.send(
                    nick,
                    'You can delete this limerick with /msg {} '
                    'deletelimerick {}'.format(
                        self.nick,
                        deletion_key
                    )
                )
            return

        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='limerick')
        )

    def command_limerickby(self, user, nick, channel, rest):
        """Display a random limerick submitted by the given nick"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='limerick', by=rest)
        )

    def command_limerickwith(self, user, nick, channel, rest):
        """Display a random limerick with the given text"""
        self.reply(
            channel,
            nick,
            self.get_random_poem(poem_type='limerick', contains=rest)
        )

    def command_deletelimerick(self, user, nick, channel, rest):
        """Delete a limerick using the deletion key."""
        deleted = self.delete_poem('limerick', rest.strip())
        if deleted:
            self.reply(channel, nick, 'Deleted Limerick!')
        else:
            self.reply(
                channel,
                nick,
                'Could not find haiku with that deletion key :('
            )

    def admin_allpoems(self, user, nick, channel, rest):
        with self.getDbSession() as db_session:
            poems = db_session.query(Poem).all()
            for poem in poems:
                print(poem.id, poem.content, poem.times_served)

    def admin_recentpoems(self, user, nick, channel, rest):
        """
        Get information on the recently displayed poems (helpful
        for moderating).
        """
        with self.getDbSession() as db_session:

            if len(self.recent_poem_ids) == 0:
                return self.reply(channel, nick, 'No recent poems displayed')

            poems = db_session.query(Poem).filter(
                Poem.id.in_(self.recent_poem_ids)
            )

            poem_map = {poem.id: poem for poem in poems.all()}

            for poem_id in self.recent_poem_ids:
                poem = poem_map.get(poem_id, None)
                if poem:
                    message = poem.get_display_message(
                        include_deletion_key=True
                    )
                    self.send(nick, message)
