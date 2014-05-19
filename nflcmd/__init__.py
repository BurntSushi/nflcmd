"""
Module nflcmd provides functions and types that are useful for building new
commands. For example, this includes formatting specifications for tables of
data, functions for aligning tabular data, and querying nfldb for aggregate
statistics quickly.
"""

import nfldb

columns = {
    'game': {
        'passer': ['passing_cmp', 'passing_att', 'passing_ratio',
                   'passing_yds', 'passing_yds_att', 'passing_tds',
                   'passing_int',
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
        'passer': ['passing_cmp', 'passing_att', 'passing_ratio',
                   'passing_yds', 'passing_yds_att', 'passing_yds_game',
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
"""
Specifies the columns to show for game and season logs.
"""

_epos = nfldb.Enums.player_pos
pcolumns = {
    _epos.QB: 'passer',
    _epos.RB: 'rusher', _epos.FB: 'rusher',
    _epos.WR: 'receiver', _epos.TE: 'receiver',
    _epos.K: 'kicker',
    _epos.P: 'punter',
}
"""
Maps positions to column list names.
"""
_defense_pos = ['C', 'CB', 'DB', 'DE', 'DL', 'DT', 'FS', 'G', 'ILB', 'LB',
                'LS', 'MLB', 'NT', 'OG', 'OL', 'OLB', 'OT', 'SAF', 'SS', 'T',
                ]
for pos in _defense_pos:
    pcolumns[_epos[pos]] = 'defender'


statfuns = {
    'passing_ratio': lambda p: percent(p.passing_cmp, p.passing_att),
    'passing_yds_att': lambda p: ratio(p.passing_yds, p.passing_att),
    'rushing_yds_att': lambda p: ratio(p.rushing_yds, p.rushing_att),
    'receiving_yds_att': lambda p: ratio(p.receiving_yds, p.receiving_rec),
    'fgm_ratio': lambda p: percent(p.kicking_fgm, p.kicking_fga),
    'xpm_ratio': lambda p: percent(p.kicking_xpmade, p.kicking_xpa),
    'defense_tkl_tot': lambda p: p.defense_tkl + p.defense_ast,
}
"""
A dictionary of derived statistics. Any of the keys in this
dictionary may be used in `nflcmd.columns` and `nflcmd.abbrev`.
"""

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

    # Misc.
    'name': 'Player', 'team': 'Team',
}
"""
Abbreviations for statistical fields. (Used in the header of tables.)
"""


class Game (object):
    """
    Represents a row of player statistics corresponding to a single
    game.
    """
    @staticmethod
    def make(db, player, game):
        """
        Create a new `nflcmd.Game` object from `nfldb.Player` and
        `nfldb.Game` objects.
        """
        pstat = game_stats(db, game, player)
        team = player_team_in_game(db, game, player)
        return Game(db, game, team, pstat)

    def __init__(self, db, game, team, pstat):
        self._db = db
        self._game = game
        self.team = team
        self._pstat = pstat
        self._fgs = None

    @property
    def fgs(self):
        if self._fgs is None:
            q = nfldb.Query(self._db)
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


class Games (object):
    """
    Represents a row of player statistics corresponding to multiple
    games.
    """
    def __init__(self, db, year, games, pstat):
        self._db = db
        self.year = year
        self.games = games
        self._pstat = pstat
        self._fgs = None

    @property
    def fgs(self):
        if self._fgs is None:
            q = nfldb.Query(self._db)
            q.play(gsis_id=[g.gsis_id for g in self.games])
            q.play(player_id=self.player_id, kicking_fga=1)
            self._fgs = q.as_play_players()
        return self._fgs

    @property
    def passing_yds_game(self):
        return ratio(self.passing_yds, len(self.games))

    @property
    def name(self):
        return self.player.full_name

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
    def team(self):
        return self.player.team

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


def game_stats(db, game, player):
    """
    Returns aggregate statistics for a particular `nfldb.Player` in a
    single `nfldb.Game`.
    """
    q = nfldb.Query(db).game(gsis_id=game.gsis_id)
    q.player(player_id=player.player_id)
    return q.as_aggregate()[0]


def search(db, name, team, pos, soundex=False):
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
    if ' ' not in name:
        for p, _ in matches:
            if name.lower() in map(str.lower, [p.first_name, p.last_name]):
                return p
    return matches[0][0]


def percent(num, den):
    """
    Returns the percentage of integers `num` and `den`.
    """
    try:
        return 100 * (float(num) / float(den))
    except ZeroDivisionError:
        return 0.0


def ratio(num, den):
    """
    Returns the ratio of integers `num` and `den`.
    """
    try:
        return float(num) / float(den)
    except ZeroDivisionError:
        return 0.0


def fg_made(p):
    """
    Returns `True` if and only if `p` corresponds to a made field goal.
    """
    return p.kicking_fgm == 1


def fgs_range(fg_plays, start, end):
    """
    Given a list of field goal `nfldb.PlayPlayer` objects, return only
    the field goals in the range `[start, end]`.
    """
    def pred(p):
        if p.kicking_fgm == 1:
            return start <= p.kicking_fgm_yds <= end
        return start <= p.kicking_fgmissed_yds <= end
    return filter(pred, fg_plays)


def query_games(db, player, year, stype, week_range=None):
    """
    Returns a `nfldb.Query` corresponding to a list of games matching
    a particular season, season phase and an optional range of weeks.
    `player` should be a `nfldb.Player` object.
    """
    q = nfldb.Query(db).game(season_year=year, season_type=stype)
    if week_range is not None:
        q.game(week=week_range)
    q.player(player_id=player.player_id)
    q.sort(('gsis_id', 'asc'))
    return q


def player_team_in_game(db, game, player):
    """
    Returns the team that the `nfldb.Player` belonged to in a
    particular `nfldb.Game`.
    """
    q = nfldb.Query(db).game(gsis_id=game.gsis_id)
    q.player(player_id=player.player_id)
    q.limit(1)
    return q.as_play_players()[0].team


def pstat_to_row(spec, pstat):
    """
    Transforms a player statistic to a list of strings corresponding
    to the given spec. Note that `pstat` should be like a
    `nfldb.PlayPlayer` object.
    """
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


def header_row(spec):
    """
    Returns a list of strings corresponding to the header row of a
    particular `spec`.
    """
    header = []
    for column in spec:
        header.append(abbrev.get(column, column))
    return header


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

def arg_range(arg, lo, hi):
    """
    Given a string of the format `[int][-][int]`, return a list of
    integers in the inclusive range specified. Open intervals are
    allowed, which will be capped at the `lo` and `hi` values given.

    If `arg` is empty or only contains `-`, then all integers in the
    range `[lo, hi]` will be returned.
    """
    arg = arg.strip()
    if len(arg) == 0 or arg == '-':
        return range(lo, hi+1)
    if '-' not in arg:
        return [int(arg)]
    start, end = map(str.strip, arg.split('-'))
    if len(start) == 0:
        return range(lo, int(end)+1)
    elif len(end) == 0:
        return range(int(start), hi+1)
    else:
        return range(int(start), int(end)+1)
