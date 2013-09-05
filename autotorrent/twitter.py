# -*- coding: utf8 -*-
import sys
import json
import optparse

import tweepy
import webbrowser


CONSUMER_KEY = "nHAcvJqC2cbcXkOswc5A"
CONSUMER_SECRET = "de3waUxG2iYoPURAQs5KGBhNlv8weFRsVw5bCDsBTo"


def notify(settings, episodes):
    for key in ("consumer_key", "consumer_secret", "access_token_key",
                "access_token_secret", "users"):
        if key not in settings:
            sys.stderr.write("Your twitter settings look incomplete, "
                             "the '%s' entry is missing.\n" % key)
            return
    auth = tweepy.OAuthHandler(settings['consumer_key'],
                               settings['consumer_secret'])
    auth.set_access_token(settings['access_token_key'],
                          settings['access_token_secret'])
    api = tweepy.API(auth)

    message = ("New episodes are available:\n" +
               "\n".join(str(episode) for episode in episodes))

    for user in settings['users']:
        try:
            api.send_direct_message(user=user, text=message)
        except tweepy.TweepError as e:
            sys.stderr.write("Notifying @%s failed: %s\n" %
                             (user, e.message))


def get_access_token(consumer_key, consumer_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        sys.stderr.write("Failed to get request token from Twitter.\n")
        sys.exit(1)
    print ("Visit %s in your web browser and authorize this application." %
           redirect_url)
    print "Note that you can't send direct messages to yourself,",
    print "you have to create a new Twitter account."
    print "Also make sure to follow this new account, otherwise you won't",
    print "get any direct messages."
    auto_open = raw_input(
        "Do you want to open your default web browser automatically? [y/N]: "
    )
    if auto_open.lower() == "y":
        webbrowser.open(redirect_url)
    pin = raw_input("Enter the PIN Twitter gave you here: ")
    try:
        auth.get_access_token(pin)
    except tweepy.TweepError:
        sys.stderr.write("Failed to get access token from Twitter.\n")
        sys.exit(1)
    return auth.access_token


if __name__ == "__main__":
    usage = ("%prog [options] user [user [...]]\n\n"
             "This script generates a settings file which can be used by"
             " autotorrent to notify the specified Twitter users via direct"
             " message when new episodes are available.\n"
             "By default the autotorrent Twitter application is used, if you"
             " are concerned for your privacy you can of course use your own"
             " application.")
    parser = optparse.OptionParser(usage=usage, prog="autotorrent.twitter")
    parser.add_option("-k", "--consumer-key", dest="consumer_key",
                      metavar="<key>", default=None,
                      help="Consumer key of your application "
                      "(uses autotorrent application by default)")
    parser.add_option("-s", "--consumer-secret", dest="consumer_secret",
                      metavar="<secret>", default=None,
                      help="Consumer secret of your application "
                      "(uses autotorrent application by default)")
    parser.add_option("-f", "--file", dest="file",
                      default=None, metavar="<path>",
                      help="Store the settings directly in a file")

    (opts, args) = parser.parse_args()

    if not args:
        parser.error(
            "You have to provide at least one user to send messages to."
        )

    if (opts.consumer_key is None) ^ (opts.consumer_secret is None):
        parser.error("You have to provide a consumer secret and a consumer key"
                     " or neither of them.")
    if opts.consumer_key is None:
        opts.consumer_key = CONSUMER_KEY
        opts.consumer_secret = CONSUMER_SECRET

    access_token = get_access_token(opts.consumer_key, opts.consumer_secret)

    settings = json.dumps({
        "consumer_key": opts.consumer_key,
        "consumer_secret": opts.consumer_secret,
        "access_token_key": access_token.key,
        "access_token_secret": access_token.secret,
        "users": args
    }, indent=4, sort_keys=True)

    if opts.file is not None:
        with open(opts.file, "w") as f:
            f.write(settings)
        print "Your settings have been saved to the specified file."
    else:
        print "Store these settings in a file and use autotorrent's --twitter",
        print "option to receive notifications when new shows are added."
        print
        print settings
