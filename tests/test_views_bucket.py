# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test bucket related views."""

from __future__ import absolute_import, print_function

from flask import url_for
from testutils import login_user

from invenio_files_rest.models import ObjectVersion


def test_head(client, headers, bucket, permissions):
    """Test checking existence of bucket."""
    cases = [
        (None, 404),
        ('auth', 404),
        ('objects', 404),  # TODO - return 403 instead
        ('bucket', 200),
        ('location', 200),
    ]

    for user, expected in cases:
        login_user(client, permissions[user])
        # Existing bucket
        resp = client.head(
            url_for('invenio_files_rest.bucket_api', bucket_id=bucket.id),
            headers=headers,
        )
        assert resp.status_code == expected
        assert not resp.data

        # Non-existing bucket
        assert client.head(
            url_for('invenio_files_rest.bucket_api', bucket_id='invalid'),
            headers=headers,
        ).status_code == 404


def test_head_locked_deleted(client, db, headers, bucket, permissions):
    """Test checking existence of bucket."""
    bucket_url = url_for('invenio_files_rest.bucket_api', bucket_id=bucket.id)

    login_user(client, permissions['location'])

    # Locked bucket
    bucket.locked = True
    db.session.commit()
    assert client.head(bucket_url).status_code == 200

    # Deleted bucket
    bucket.deleted = True
    db.session.commit()
    assert client.head(bucket_url).status_code == 404


def test_get(client, headers, permissions, bucket, objects, get_json):
    """Test listing objects."""
    cases = [
        (None, 404),
        ('auth', 404),
        ('objects', 404),  # TODO - return 403 instead
        ('bucket', 200),
        ('location', 200),
    ]

    for user, expected in cases:
        login_user(client, permissions[user])
        # Existing bucket
        resp = client.get(url_for(
            'invenio_files_rest.bucket_api',
            bucket_id=bucket.id,
        ), headers=headers)
        assert resp.status_code == expected

        if resp.status_code == 200:
            data = get_json(resp)
            assert len(data['contents']) == 2
            assert all([x['is_head'] for x in data['contents']])

        # Non-existing bucket
        resp = client.get(url_for(
            'invenio_files_rest.bucket_api',
            bucket_id='invalid',
        ), headers=headers)
        assert resp.status_code == 404


def test_get_versions(client, headers, permissions, bucket, objects, get_json):
    """Test listing objects."""
    cases = [
        (None, 404),
        ('auth', 404),
        ('bucket', 403),  # User already knowns bucket exists.
        ('objects', 404),  # TODO - return 403 instead
        ('location', 200),
    ]

    for user, expected in cases:
        login_user(client, permissions[user])

        resp = client.get(url_for(
            'invenio_files_rest.bucket_api',
            bucket_id=bucket.id,
            versions='1',
        ), headers=headers)
        assert resp.status_code == expected

        if resp.status_code == 200:
            data = get_json(resp)
            assert len(data['contents']) == 4
            assert data['id'] == str(bucket.id)


def test_get_empty_bucket(db, client, headers, bucket, objects, permissions,
                          get_json):
    """Test getting objects from an empty bucket."""
    # Delete the objects created in the fixtures to have an empty bucket with
    # permissions set up.
    for obj in objects:
        ObjectVersion.delete(obj.bucket_id, obj.key)
    db.session.commit()

    cases = [
        (None, 404),
        ('auth', 404),
        ('objects', 404),  # TODO - return 403 instead
        ('bucket', 200),
        ('location', 200),
    ]

    for user, expected in cases:
        login_user(client, permissions[user])

        resp = client.get(
            url_for('invenio_files_rest.bucket_api', bucket_id=bucket.id),
            headers=headers
        )
        assert resp.status_code == expected
        if resp.status_code == 200:
            assert get_json(resp)['contents'] == []
