#!/usr/bin/env python
#incomingwebhook -> https://fmi-talk.slack.com/apps/A0F7XDUAZ-incoming-webhooks?page=1

'''
This script will grab the leaderboard from Advent of Code and post it to Slack
'''

import datetime, json, requests

# see README for directions on how to fill these variables
LEADERBOARD_ID = "296557"
SESSION_ID = "53616c7465645f5f10a2de9e8e87d77099588121520696411a74f4b4cfe57f06866bb8614ccd8d1b3215c9171c279d76"
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

def formatLeaderMessage(members):
    message = ""

    # add each member to message
    for username, score, stars in members:
        message += "\n*{}* {} Points, {} Stars".format(username, score, stars)

    message += "\n\n<{}|View Online Leaderboard>".format(LEADERBOARD_URL)

    return message

def parseMembers(members_json):
    # get member name, score and stars
    print(members_json.values())
    members = [(m["name"], m["l_score"], m["stars"]) for m in members_json.values()]

    # sort members by score, decending
    members.sort(key=lambda s: (-s[1], -s[2]))

    return members

def postMessage(message):
    payload = json.dumps({
        "icon_emoji": ":ghost:",
        "username": "Advent Of Code Leaderboard",
        "text": message
    })

    requests.post(
        SLACK_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

def main():
    # make sure all variables are filled
    if LEADERBOARD_ID == "" or SESSION_ID == "" or SLACK_WEBHOOK == "":
        print("Please update script variables before running script.\nSee README for details on how to do this.")
        exit(1)
    
    global LEADERBOARD_URL
    
    #LEADERBOARD_URL = "https://adventofcode.com/{}/leaderboard/private/view/{}".format(datetime.datetime.today().year, LEADERBOARD_ID)
    #print ("LEADERBOARD_URL: %s", str(LEADERBOARD_URL))
    LEADERBOARD_URL = "https://adventofcode.com/2017/leaderboard/private/view/incoming-webhook"
    #LEADERBOARD_URL = "http://adventofcode.com/2017/leaderboard/private/view/319642"
    """
    # retrieve leaderboard
    r = requests.get(
        "{}.json".format(LEADERBOARD_URL),
        cookies={"session": SESSION_ID}
    )
    print("r:", str(r))
    print("r.status_code:", str(r.status_code))
    print("requests.codes.ok:", str(requests.codes.ok))

    #if r.status_code != requests.codes.ok:
        #print("Error retrieving leaderboard")
        #exit(1)
    """
    json = {"296557":{"stars":0,"last_star_ts":"1969-12-31T19:00:00-0500","name":"Fajar N","l_score":0,"g_score":0,"level":{},"id":"296557"}}
    # get members from json
    members = parseMembers(json)

    # generate message to send to slack
    message = formatLeaderMessage(members)

    # send message to slack
    postMessage(message)

if __name__ == "__main__":
    main()