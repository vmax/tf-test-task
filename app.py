#!/usr/bin/env python
from collections import defaultdict
from datetime import datetime
from flask import Flask, render_template, request

import config
from hubstaff import HubStaff

app = Flask("app", template_folder='templates')
hs = HubStaff(config.APP_TOKEN)

# hs = HubStaff.init_with_auth_token(config.APP_TOKEN, config.AUTH_TOKEN,
#                                    config.USER_ID)


@app.before_first_request
def hs_auth():
    print('authenticating: before')
    hs.auth(config.AUTH_USERNAME, config.AUTH_PASSWORD)
    print('authenticating: end')


def transform(report):
    # Take HubStaff's report and make it a valid context dict
    organizations = report['organizations']

    if not organizations:
        return {'users': [], 'rows': []}

    data_for_day = organizations[0]['dates'][0]['users']
    names = [x['name'] for x in data_for_day]
    projects = defaultdict(dict)
    rows = []

    for row in data_for_day:
        for prj in row['projects']:
            projects[prj['name']][row['name']] = prj['duration']

    for project, times in projects.items():
        row = [project]
        for name in names:
            time = times.get(name)
            time = '{}h {}m'.format(time // 3600, time % 60) if time else '—'
            row.append(time)
        rows.append(row)

    return {'users': names,
            'rows': rows}


@app.route('/table/')
def table():
    date = request.args.get('date')
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return render_template('table.html', error='Date is wrong')
    start, end = (date.replace(hour=0, minute=0, second=0),
                  date.replace(hour=23, minute=59, second=59))

    # FIXME: this assumes that user belongs to one organization
    # and it's the exact one we're interested in
    try:
        my_organization_id = hs.my_organizations()['organizations'][0]['id']
        report = hs.custom_by_date_team_report(start, end, my_organization_id)
        print(report)
        return render_template('table.html', **transform(report))
    except Exception as e:
        return render_template('table.html', error=str(e))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
