from pywebpush import webpush, WebPushException
import json, psycopg2,requests
from flask import current_app
import postsqldb, config


def push_ntfy(title, body):
    requests.post("http://ntfy.treehousefullofstars.com/pantry", 
                    data=body,
                    headers={
                        "Title": title,
                        "Priority": "default",
                        "Tags": "tada"
                    })

def push_notifications(title, body):
    database_config = config.config()
    subscriptions = None
    with psycopg2.connect(**database_config) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM push_subscriptions;")
            subscriptions = cur.fetchall()
            trigger_push_notifications_for_subscriptions(subscriptions, title, body)

def trigger_push_notification(subscription, title, body):
    print('sub', json.loads(subscription[1]))
    try:
        response = webpush(
            subscription_info=json.loads(subscription[1]),
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
            vapid_claims={
                "sub": "mailto:{}".format(
                    current_app.config["VAPID_CLAIM_EMAIL"])
            }
        )
        print('response', response)
        return response.ok
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        print(ex)
        return False


def trigger_push_notifications_for_subscriptions(subscriptions, title, body):
    return [trigger_push_notification(subscription, title, body)
            for subscription in subscriptions]