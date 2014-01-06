nflcmd is a set of command line programs for interacting with NFL data using
[nfldb](https://github.com/BurntSushi/nfldb). This includes, but is not limited 
to, viewing game stats, season stats and ranking players by any combination of 
statistical category over any duration.

There are two main goals of this project:

* The commands should be simple with sane defaults.
* Commands should be reasonably fast.


### Documentation and getting help

Run any of the commands with the `--help` flag:

    nflstats --help
    nflrank --help

nflcmd has
[some API documentation](http://pdoc.burntsushi.net/nflcmd), but it's mostly 
only useful to developers seeking to add more commands.

If you need any help or have found a bug, please
[open a new issue on nflcmd's issue 
tracker](https://github.com/BurntSushi/nflcmd/issues/new)
or join us at our IRC channel `#nflgame` on FreeNode.


### Installation and dependencies

nflcmd depends only on [nfldb](https://pypi.python.org/nfldb), which includes 
having [a PostgreSQL database accessible to 
you](https://github.com/BurntSushi/nfldb/wiki/Installation).

I've only tested nflcmd with Python 2.7 on a Linux system. In theory, nflcmd 
should be able to work on Windows and Mac systems as long as you can get 
PostgreSQL running. It is **not** Python 3 compatible.


### Examples for `nflstats`

`nflstats` shows either game or season statistics for a player.

Show Tom Brady's stats for the current season:

    nflstats tom brady

Or for all seasons (in nfldb):

    nflstats tom brady --season

Or only show his stats for the first four weeks of the 2011 season:

    nflstats tom brady --year 2011 --weeks 1-4


### Examples for `nflrank`

`nflrank` shows player rankings on one or more statistical categories.

Show the leading touchdown passers for the 2010 season:

    nflrank passing_tds --years 2010

Or for all seasons from 2009 to the current season:

    nflrank passing_tds --years 2009-

The same, but restricted to just the first four weeks of each season:

    nflrank passing_tds --years 2009- --weeks 1-4

Show the rushing leaders for the Patriots in the 2013 season, ranked first by 
touchdowns and then by rushing yards:

    nflrank rushing_tds rushing_yds --teams NE

Show the most targeted receivers of the 2012 postseason:

    nflrank receiving_tar --years 2012 --post

Or the running backs who can't hold on to the ball in the current season:

    nflrank fumbles_lost --pos RB

Or the guys who are best at stripping the ball:

    nflrank defense_ffum

Or the guys who are best at returning interceptions:

    nflrank defense_int_yds defense_int

