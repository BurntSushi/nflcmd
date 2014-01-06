from __future__ import absolute_import, division, print_function
import argparse
from functools import partial
import sys

import nfldb

db = nfldb.connect()
_, cur_year, _ = nfldb.current(db)

class Game (object):
    @staticmethod
    def make(player, game):
        pstat = game_stats(game, player)
        team = player_team_in_game(game, player)
        return Game(game, team, pstat)

    def __init__(self, game, team, pstat):
        self._game = game
        self.team = team
        self._pstat = pstat
        self._fgs = None

    @property
    def fgs(self):
        if self._fgs is None:
            q = nfldb.Query(db)
            q.play(gsis_id=self.gsis_id, player_id=self.player_id)
            q.play(kicking_fga=1)
            self._fgs = q.as_play_players()
        return self._fgs

    @property
    def fg_0_29(self):
        fgs = fgs_range(self.fgs, 0, 29)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_30_39(self):
        fgs = fgs_range(self.fgs, 30, 39)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_40_49(self):
        fgs = fgs_range(self.fgs, 40, 49)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_50(self):
        fgs = fgs_range(self.fgs, 50, 100)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def outcome(self):
        if self._game is None:
            return '-'
        return 'W' if self.team == self.winner else 'L'

    @property
    def game_date(self):
        if self._game is None:
            return '-'
        return '{d:%b} {d.day}'.format(d=self.start_time)

    @property
    def opp(self):
        if self._game is None:
            return '-'
        if self.team == self.away_team:
            return '@' + self.home_team
        return self.away_team

    def __getattr__(self, k):
        try:
            return getattr(self._game, k)
        except AttributeError:
            try:
                return getattr(self._pstat, k)
            except AttributeError:
                return '-'

class Season (object):
    def __init__(self, year, games, pstat):
        self.year = year
        self.games = games
        self._pstat = pstat
        self._fgs = None

    @property
    def fgs(self):
        if self._fgs is None:
            q = nfldb.Query(db)
            q.play(gsis_id=[g.gsis_id for g in self.games])
            q.play(player_id=self.player_id, kicking_fga=1)
            self._fgs = q.as_play_players()
        return self._fgs

    @property
    def passing_yds_game(self):
        return ratio(self.passing_yds, len(self.games))

    @property
    def passing_300(self):
        return len(filter(lambda p: p.passing_yds >= 300, self.games))

    @property
    def fg_0_29(self):
        fgs = fgs_range(self.fgs, 0, 29)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_30_39(self):
        fgs = fgs_range(self.fgs, 30, 39)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_40_49(self):
        fgs = fgs_range(self.fgs, 40, 49)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def fg_50(self):
        fgs = fgs_range(self.fgs, 50, 100)
        return '%d/%d' % (len(filter(fg_made, fgs)), len(fgs))

    @property
    def game_count(self):
        return len(self.games)

    @property
    def teams(self):
        teams = []
        for g in self.games:
            if len(teams) == 0 or teams[-1] != g.team:
                teams.append(g.team)
        return '/'.join(teams)

    def __getattr__(self, k):
        try:
            return getattr(self._pstat, k)
        except AttributeError:
            return '-'

def eprint(*args, **kwargs):
    """
    Print to stderr.
    """
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def search(name, team, pos, soundex=False):
    """
    Provides a thin wrapper over nfldb's player search. Namely, if
    `name` is one word, then it assumes that it's a first/last name and
    tries to match it exactly against the list of results returned from
    the Levenshtein/Soundex search.
    """
    matches = nfldb.player_search(db, name, team, pos,
                                  limit=100, soundex=soundex)
    if len(matches) == 0:
        return None
    # for p, d in matches: print(p, d) 
    if ' ' not in name:
        for p, _ in matches:
            if name.lower() in map(str.lower, [p.first_name, p.last_name]):
                return p
    return matches[0][0]

def percent(num, den):
    try:
        return 100 * (float(num) / float(den))
    except ZeroDivisionError:
        return 0.0

def ratio(num, den):
    try:
        return float(num) / float(den)
    except ZeroDivisionError:
        return 0.0

def fg_made(p):
    return p.kicking_fgm == 1

def fgs_range(fg_plays, start, end):
    def pred(p):
        if p.kicking_fgm == 1:
            return start <= p.kicking_fgm_yds <= end
        return start <= p.kicking_fgmissed_yds <= end
    return filter(pred, fg_plays)

def query_games(player, year, stype, week_range=None):
    """
    Returns a list of games matching a particular season, season phase
    and an optional range of weeks. `player` should be a `nfldb.Player`
    object.
    """
    q = nfldb.Query(db).game(season_year=year, season_type=stype)
    if week_range is not None:
        q.game(week=week_range)
    q.player(player_id=player.player_id)
    q.sort(('gsis_id', 'asc'))
    return q

def game_stats(game, player):
    q = nfldb.Query(db).game(gsis_id=game.gsis_id)
    q.player(player_id=player.player_id)
    return q.as_aggregate()[0]

def player_team_in_game(game, player):
    q = nfldb.Query(db).game(gsis_id=game.gsis_id)
    q.play(player_id=player.player_id)
    q.limit(1)
    return q.as_play_players()[0].team

def show_game_table(player, year, stype, week_range=None, pos=None):
    if pos is None:
        pos = player.position

    games = query_games(player, year, stype, week_range).as_games()
    pstats = map(partial(Game.make, player), games)
    spec = columns['game'][pcolumns[pos]]
    show_table(player, pstats, columns['game']['prefix'] + spec)

def show_season_table(player, stype, week_range=None, pos=None):
    if pos is None:
        pos = player.position

    pstats = []
    for year in range(2009, cur_year+1):
        qgames = query_games(player, year, stype, week_range)
        games = qgames.as_games()
        if len(games) == 0:
            continue

        game_stats = map(partial(Game.make, player), games)
        agg = qgames.sort([]).as_aggregate()
        pstats.append(Season(year, game_stats, agg[0]))

    spec = columns['season'][pcolumns[pos]]
    show_table(player, pstats, columns['season']['prefix'] + spec)

def show_table(p, pstats, spec):
    """
    Prints a table of statistics to stdout. `p` should be a
    `nfldb.Player` object, `pstats` should be a list of `Game` or
    `Season` objects, and `spec` should be a list of attributes to show
    for each row.

    If `pstats` is empty, then a message will be printed saying that no
    statistics could be found.
    """
    def pstat_to_row(pstat):
        row = []
        for column in spec:
            v = 0
            if column in statfuns:
                v = statfuns[column](pstat)
            else:
                v = getattr(pstat, column)
            if isinstance(v, float):
                row.append('%0.1f' % v)
            else:
                row.append(v)
        return row

    if len(pstats) == 0:
        print('No statistics found given the criteria.')
        return

    rows = []
    header = []
    for column in spec:
        header.append(abbrev.get(column, column))

    rows.append(header)
    rows += map(pstat_to_row, pstats)

    if len(pstats) > 1:
        summary = nfldb.aggregate(pstat._pstat for pstat in pstats)[0]
        if isinstance(pstats[0], Game):
            allrows = Game(None, '-', summary)
            allrows._fgs = []
            for pstat in pstats:
                allrows._fgs += pstat.fgs
        elif isinstance(pstats[0], Season):
            allrows = Season('-', [], summary)
            allrows._fgs = []
            for pstat in pstats:
                allrows._fgs += pstat.fgs
                allrows.games += pstat.games
        rows.append(pstat_to_row(allrows))
    print(table(rows))

def table(lst):
    """
    Takes a list of iterables and returns them as a nicely formatted table.

    All values must be convertible to a str, or else a ValueError will
    be raised.

    N.B. I thought Python's standard library had a module that did this
    (or maybe it was Go's standard library), but I'm on an airplane and
    pydoc sucks.
    """
    pad = 2
    maxcols = []
    output = []
    first_row = True
    for row in lst:
        if row is None:
            output.append([])
            continue

        output_row = []
        for i, cell in enumerate(row):
            cell = str(cell)
            if first_row:
                maxcols.append(len(cell) + pad)
            else:
                maxcols[i] = max([maxcols[i], len(cell) + pad])
            output_row.append(cell)

        output.append(output_row)
        first_row = False

    rowsep = '-' * sum(maxcols)
    nice = []
    for i, row in enumerate(output):
        nice_row = []
        for j, cell in enumerate(row):
            nice_row.append(cell.rjust(maxcols[j]))
        nice.append(''.join(nice_row))
        if i < len(output) - 1:
            nice.append(rowsep)

    return '\n'.join(nice)

# Specifies the columns to show for game and season logs.
columns = {
    'game': {
        'prefix': ['week', 'outcome', 'game_date', 'opp'],
        'passer': ['passing_cmp', 'passing_att', 'passing_ratio', 'passing_yds',
                   'passing_yds_att', 'passing_tds', 'passing_int',
                   'rushing_att', 'rushing_yds', 'rushing_yds_att',
                   'rushing_tds', 'fumbles_lost',
                  ],
        'rusher': ['rushing_att', 'rushing_yds', 'rushing_yds_att',
                   'rushing_tds',
                   'receiving_rec', 'receiving_tar', 'receiving_yds',
                   'receiving_yds_att', 'receiving_tds',
                   'fumbles_lost',
                   'kickret_yds', 'kickret_tds',
                   'puntret_yds', 'puntret_tds',
                  ],
        'receiver': ['receiving_rec', 'receiving_tar', 'receiving_yds',
                     'receiving_yds_att', 'receiving_yac_yds', 'receiving_tds',
                     'rushing_att', 'rushing_yds', 'rushing_yds_att',
                     'rushing_tds',
                     'fumbles_lost',
                     'kickret_yds', 'kickret_tds',
                     'puntret_yds', 'puntret_tds',
                    ],
        'kicker': ['fg_0_29', 'fg_30_39', 'fg_40_49', 'fg_50',
                   'kicking_fgm', 'kicking_fga', 'fgm_ratio',
                   'kicking_xpmade', 'kicking_xpa', 'xpm_ratio',
                   'kicking_touchback',
                  ],
        'punter': ['punting_tot', 'punting_yds', 'punting_touchback',
                  ],
        'defender': ['defense_tkl', 'defense_ast', 'defense_tkl_tot',
                     'defense_sk', 'defense_sk_yds',
                     'defense_int', 'defense_int_yds', 'defense_int_tds',
                     'defense_frec', 'defense_frec_tds', 'defense_ffum',
                     'defense_pass_def', 'defense_safe',
                     'kickret_yds', 'kickret_tds',
                     'puntret_yds', 'puntret_tds',
                    ],
    },
    'season': {
        'prefix': ['year', 'teams', 'game_count'],
        'passer': ['passing_cmp', 'passing_att', 'passing_ratio', 'passing_yds',
                   'passing_yds_att', 'passing_yds_game',
                   'passing_300', 'passing_tds', 'passing_int',
                   'rushing_att', 'rushing_yds', 'rushing_yds_att',
                   'rushing_tds', 'fumbles_lost',
                  ],
        'rusher': ['rushing_att', 'rushing_yds', 'rushing_yds_att',
                   'rushing_tds',
                   'receiving_rec', 'receiving_tar', 'receiving_yds',
                   'receiving_yds_att', 'receiving_tds',
                   'fumbles_lost',
                   'kickret_yds', 'kickret_tds',
                   'puntret_yds', 'puntret_tds',
                  ],
        'receiver': ['receiving_rec', 'receiving_tar', 'receiving_yds',
                     'receiving_yds_att', 'receiving_yac_yds', 'receiving_tds',
                     'rushing_att', 'rushing_yds', 'rushing_yds_att',
                     'rushing_tds',
                     'fumbles_lost',
                     'kickret_yds', 'kickret_tds',
                     'puntret_yds', 'puntret_tds',
                    ],
        'kicker': ['fg_0_29', 'fg_30_39', 'fg_40_49', 'fg_50',
                   'kicking_fgm', 'kicking_fga', 'fgm_ratio',
                   'kicking_xpmade', 'kicking_xpa', 'xpm_ratio',
                   'kicking_touchback',
                  ],
        'punter': ['punting_tot', 'punting_yds', 'punting_touchback',
                  ],
        'defender': ['defense_tkl', 'defense_ast', 'defense_tkl_tot',
                     'defense_sk', 'defense_sk_yds',
                     'defense_int', 'defense_int_yds', 'defense_int_tds',
                     'defense_frec', 'defense_frec_tds', 'defense_ffum',
                     'defense_pass_def', 'defense_safe',
                     'kickret_yds', 'kickret_tds',
                     'puntret_yds', 'puntret_tds',
                    ],
    },
}

# Maps positions to column list names.
epos = nfldb.Enums.player_pos
pcolumns = {
    epos.QB: 'passer',
    epos.RB: 'rusher', epos.FB: 'rusher',
    epos.WR: 'receiver', epos.TE: 'receiver',
    epos.K: 'kicker',
    epos.P: 'punter',
}
defense_pos = ['C', 'CB', 'DB', 'DE', 'DL', 'DT', 'FS', 'G', 'ILB', 'LB', 'LS',
               'MLB', 'NT', 'OG', 'OL', 'OLB', 'OT', 'SAF', 'SS', 'T',
              ]
for pos in defense_pos:
    pcolumns[epos[pos]] = 'defender'

# Custom statistics.
statfuns = {
    'passing_ratio': lambda p: percent(p.passing_cmp, p.passing_att),
    'passing_yds_att': lambda p: ratio(p.passing_yds, p.passing_att),
    'rushing_yds_att': lambda p: ratio(p.rushing_yds, p.rushing_att),
    'receiving_yds_att': lambda p: ratio(p.receiving_yds, p.receiving_rec),
    'fgm_ratio': lambda p: percent(p.kicking_fgm, p.kicking_fga),
    'xpm_ratio': lambda p: percent(p.kicking_xpmade, p.kicking_xpa),
    'defense_tkl_tot': lambda p: p.defense_tkl + p.defense_ast,
}

# Abbreviations for statistical fields. (Used in the header of tables.)
abbrev = {
    'passing_cmp': 'CMP', 'passing_att': 'P Att', 'passing_ratio': '%',
    'passing_yds': 'P Yds', 'passing_yds_att': 'Y/Att',
    'passing_yds_game': 'Y/G', 'passing_300': '300+',
    'passing_tds': 'P TDs', 'passing_int': 'INT',
    'rushing_att': 'R Att', 'rushing_yds': 'R Yds', 'rushing_yds_att': 'Y/Att',
    'rushing_tds': 'R TDs',
    'receiving_tar': 'WR Tar', 'receiving_rec': 'WR Rec',
    'receiving_yds': 'WR Yds', 'receiving_yds_att': 'Y/Att',
    'receiving_yac_yds': 'YAC',
    'receiving_tds': 'WR TDs',
    'fumbles_lost': 'F Lost',
    'kickret_yds': 'KR Yds', 'kickret_tds': 'KR TDs',
    'puntret_yds': 'PR Yds', 'puntret_tds': 'PR TDs',
    'fg_0_29': '0-29 M/A', 'fg_30_39': '30-39 M/A',
    'fg_40_49': '40-49 M/A', 'fg_50': '50+ M/A',
    'kicking_fgm': 'FGM', 'kicking_fga': 'FGA', 'fgm_ratio': '%',
    'kicking_xpmade': 'XPM', 'kicking_xpa': 'XPA', 'xpm_ratio': '%',
    'kicking_touchback': 'TBs',
    'punting_tot': 'Punts', 'punting_yds': 'Yards', 'punting_touchback': 'TBs',

    'defense_tkl': 'Solo', 'defense_ast': 'Ast', 'defense_tkl_tot': 'Total',
    'defense_sk': 'SK', 'defense_sk_yds': 'SK Yds',
    'defense_int': 'Int', 'defense_int_yds': 'Int Yds',
    'defense_int_tds': 'Int TDs',
    'defense_frec': 'F Rec', 'defense_frec_tds': 'F Rec TDs',
    'defense_ffum': 'F Forced',
    'defense_pass_def': 'Pass def', 'defense_safe': 'Safe',

    # Prefixes for game logs
    'week': 'Week', 'outcome': 'W/L', 'game_date': 'Date', 'opp': 'OPP',

    # Prefixes for season logs
    'year': 'Year', 'teams': 'Team', 'game_count': 'G',
}

def run():
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
    aa('--weeks', type=str, default=None,
       help='Specify an inclusive range of weeks for the game log. e.g., 5-8. '
            'Has no effect when --season is used.')
    aa('--season', action='store_true',
       help='When set, statistics are shown by season instead of by game.')
    aa('--show-as', type=str, default=None,
       help='Force display of player as a particular position. This must be '
            'set for inactive players.')
    args = parser.parse_args()

    args.player_query = ' '.join(args.player_query)
    player = search(args.player_query, args.team, args.pos, args.soundex)
    if player is None:
        eprint("Could not find a player given the criteria.")
        sys.exit(1)
    print('Player matched: %s' % player)

    stype = 'Regular'
    if args.pre:
        stype = 'Preseason'
    if args.post:
        stype = 'Postseason'

    week_range = None
    if args.weeks is not None and '-' in args.weeks:
        start, end = map(int, args.weeks.split('-'))
        week_range = range(start, end+1)

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
                   "his position. Please specify it with the '--show-as' flag.")
            sys.exit(1)
        print("Guessed position: %s" % pos)

    if args.season:
        show_season_table(player, stype, week_range, pos)
    else:
        show_game_table(player, args.year, stype, week_range, pos)
