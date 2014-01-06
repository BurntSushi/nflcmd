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
    aa('--pos', type=str, default=[], nargs='+',
       help='When set, only show players in the given positions.')
    aa('--teams', type=str, default=[], nargs='+',
       help='When set, only show players currently on the given teams.')
    args = parser.parse_args()

    stype = 'Regular'
    if args.pre:
        stype = 'Preseason'
    if args.post:
        stype = 'Postseason'

    years = nflcmd.arg_range(args.years, 2009, cur_year)
    weeks = nflcmd.arg_range(args.weeks, 1, 17)

    def to_games(agg):
        syrs = years[0] if len(years) == 1 else '%d-%d' % (years[0], years[-1])
        qgames = nflcmd.query_games(db, agg.player, years, stype, weeks)
        return nflcmd.Games(db, syrs, qgames.as_games(), agg)

    catq = nfldb.QueryOR(db)
    for cat in args.categories:
        k = cat + '__ne'
        catq.play(**{k: 0})

    q = nfldb.Query(db)
    q.game(season_year=years, season_type=stype, week=weeks)
    q.andalso(catq)
    if len(args.pos) > 0:
        posq = nfldb.QueryOR(db)
        for pos in args.pos:
            posq.player(position=nfldb.Enums.player_pos[pos])
        q.andalso(posq)
    if len(args.teams) > 0:
        q.player(team=args.teams)
    q.sort([(cat, 'desc') for cat in args.categories])
    q.limit(10)
    pstats = map(to_games, q.as_aggregate())

    spec = ['name', 'team', 'game_count'] + args.categories
    rows = [nflcmd.header_row(spec)]
    rows += map(partial(nflcmd.pstat_to_row, spec), pstats)
    print(nflcmd.table(rows))
