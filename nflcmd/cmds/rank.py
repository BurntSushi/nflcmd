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
    nflcmd.show_table(db, player, pstats,
                      nflcmd.columns['game']['prefix'] + spec,
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
    nflcmd.show_table(db, player, pstats,
                      nflcmd.columns['season']['prefix'] + spec,
                      summary=True)


def run():
    """Runs the `nflstats` command."""
    db = nfldb.connect()
    _, cur_year, _ = nfldb.current(db)

    parser = argparse.ArgumentParser(
        description='Show NFL player rankings for statistical categories.')
    aa = parser.add_argument
    aa(dest='categories', metavar='CATEGORY', nargs='+')
    aa('--years', type=str, default=str(cur_year),
       help='Show rankings only for the inclusive range of years given,\n'
            'e.g., "2010-2011". Other valid examples: "2010", "-2010",\n'
            '"2010-".')
    aa('--weeks', type=str, default='',
       help='Show rankings only for the inclusive range of weeks given,\n'
            'e.g., "4-8". Other valid examples: "4", "-8",\n'
            '"4-".')
    aa('--pre', action='store_true',
       help='When set, only data from the preseason will be used.')
    aa('--post', action='store_true',
       help='When set, only data from the postseason will be used.')
    aa('--show-as', type=str, default=None,
       help='Force display of rankings as a particular position. This may '
            'need to be for inactive players.')
    args = parser.parse_args()

    stype = 'Regular'
    if args.pre:
        stype = 'Preseason'
    if args.post:
        stype = 'Postseason'

    # pos = None 
    # if args.show_as is not None: 
        # pos = nfldb.Enums.player_pos[args.show_as] 

    years = nflcmd.arg_range(args.years, 2009, cur_year)
    weeks = nflcmd.arg_range(args.weeks, 1, 17)

    q = nfldb.Query(db)
    q.game(season_year=years, season_type=stype, week=weeks)
    q.play(passing_yds__ne=0)
    q.sort(('passing_yds', 'desc'))
    q.limit(10)

    def to_games(agg):
        syrs = years[0] if len(years) == 1 else '%d-%d' % (years[0], years[-1])
        return nflcmd.Games(db, syrs, [], agg)

    spec = ['name', 'team'] + nflcmd.columns['season']['passer']
    nflcmd.show_table(db, map(to_games, q.as_aggregate()), spec)
