Example Configuration File
============================================

To learn more about each option, check out the :doc:`settings` section.

Here is what user configuration file looks like with all available options set: ::

    General:
        keep_files: no
        keep_if_skips: yes

    Deluge:
        enabled: yes
        host: 192.168.1.6
        port: 58846
        user: deluge
        pass: deluge1

    Logging:
        enabled: yes
        level: 30
        log_file: /home/admin/logs/mediahandler.log

    Notifications:
        enabled: yes
        notify_name: Home Server
        pushover:
            api_key: snOLInvm7VIBSySbBL9ae1MZmF1xoM
            user_key: utTsCTaOab5FWkoQR4aaCrWtajyWy0
        pushbullet:
            token: xwl2Iex4FRaVVfEMzbvW814G96d3diRY

    TV:
        enabled: yes
        folder: /home/admin/media/television
        ignore_subs: yes
        format: "{n}/Season {s}/{n.space('.')}.{'S'+s.pad(2)}E{e.pad(2)}"
        log_file: /home/admin/logs/mediahandler-tv.log

    Movies:
        enabled: yes
        folder: /home/admin/media/movies
        ignore_subs: yes
        format: "{n} ({y})"
        log_file: /home/admin/logs/mediahandler-movies.log

    Music:
        enabled: yes
        log_file: /home/admin/logs/mediahandler-music.log

    Audiobooks:
        enabled: yes
        folder: /home/admin/media/books
        api_key: fbqkyzSfPD0j51gnCeZVNZzBHk576_8PHkSAMHT
        make_chapters: on
        chapter_length: 8
