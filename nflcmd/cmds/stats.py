from __future__ import absolute_import, division, print_function
import argparse
from functools import partial
import sys

import nfldb

import nflcmd


__all__ = ['run']


def eprint(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def show_game_table(db, player, year, stype, week_range=None, pos=None):
    if pos is None:
        pos = player.position

    games = nflcmd.query_games(db, player, year, stype, week_range).as_games()
    pstats = map(partial(nflcmd.Game.make, db, player), games)
    spec = nflcmd.columns['game'][nflcmd.pcolumns[pos]]
    nflcmd.show_table(db, pstats, nflcmd.columns['game']['prefix'] + spec,
                      summary=True)


def show_season_table(db, player, stype, week_range=None, pos=None):
    if pos is None:
        pos = player.position
    _, cur_year, _ = nfldb.current(db)

    pstats = []
    for year in range(2009, cur_year+1):
        qgames = nflcmd.query_games(db, player, year, stype, week_range)
        games = qgames.as_games()
        if len(games) == 0:
            continue

        game_stats = map(partial(nflcmd.Game.make, db, player), games)
        agg = qgames.sort([]).as_aggregate()
        pstats.append(nflcmd.Games(db, year, game_stats, agg[0]))

    spec = nflcmd.columns['season'][nflcmd.pcolumns[pos]]
    nflcmd.show_table(db, pstats, nflcmd.columns['season']['prefix'] + spec,
                      summary=True)


def run():
    """Runs the `nflstats` command."""
    db = nfldb.connect()
    _, cur_year, _ = nfldb.current(db)

    parser = argparse.ArgumentParser(
        description='Show NFL game stats for a player.')
    aa = parser.add_argument
    aa(dest='player_query', metavar='PLAYER', nargs='+')
    aa('--team', type=str, default=None,
       help='Specify the team of the player to help the search.')
    aa('--pos', type=str, default=None,
       help='Specify the position of the player to help the search.')
    aa('--soundex', action='store_true',
       help='When set, player names are compared using Soundex instead '
            'of Levenshtein.')
    aa('--year', type=str, default=cur_year,
       help='Show game logs for only this year. (Not applicable if '
            '--season is set.)')
    aa('--pre', action='store_true',
       help='When set, only games from the preseason will be used.')
    aa('--post', action='store_true',
       help='When set, only games from the postseason will be used.')
    aa('--weeks', type=str, default='',
       help='Show stats only for the inclusive range of weeks given,\n'
            'e.g., "4-8". Other valid examples: "4", "-8",\n'
            '"4-". Has no effect when --season is used.')
    aa('--season', action='store_true',
       help='When set, statistics are shown by season instead of by game.')
    aa('--show-as', type=str, default=None,
       help='Force display of player as a particular position. This may need '
            'to be set for inactive players.')
    args = parser.parse_args()

    args.player_query = ' '.join(args.player_query)
    player = nflcmd.search(db, args.player_query, args.team, args.pos,
                           args.soundex)
    if player is None:
        eprint("Could not find a player given the criteria.")
        sys.exit(1)
    print('Player matched: %s' % player)

    week_range = nflcmd.arg_range(args.weeks, 1, 17)
    stype = 'Regular'
    if args.pre:
        stype = 'Preseason'
    if args.post:
        stype = 'Postseason'


    pos = None
    if args.show_as is not None:
        pos = nfldb.Enums.player_pos[args.show_as]
    elif player.position == nfldb.Enums.player_pos.UNK:
        q = nfldb.Query(db)
        q.play(player_id=player.player_id)
        q.sort(('gsis_id', 'desc'))
        pos = nfldb.guess_position(q.as_play_players())
        if pos == nfldb.Enums.player_pos.UNK:
            eprint("The player matched is not active and I could not guess\n"
                   "his position. Specify it with the '--show-as' flag.")
            sys.exit(1)
        print("Guessed position: %s" % pos)

    if args.season:
        show_season_table(db, player, stype, week_range, pos)
    else:
        show_game_table(db, player, args.year, stype, week_range, pos)
