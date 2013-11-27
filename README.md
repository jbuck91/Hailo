This plugin allows your supybot to use Hailo :

http://search.cpan.org/~hinrik/Hailo-0.70/lib/Hailo.pm

See config.py for details, all is disabled by default, but you can configure database per channel, learn per channel, reply when addressed per channel and random reply per channel

You should create your hailo database first :

    hailo -b /path/to/brain.sqlite
    
After being created, the database order cannot be changed, so you should try a bit between -o 2 and -o 5, rm it and try again ..
