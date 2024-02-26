# Generated by Django 4.2 on 2024-02-26 14:09

import re

from django.conf import settings
from django.db import migrations
from django.urls import NoReverseMatch, reverse

# Some users hacked uMap to use another map datalayer as a remote data source.
# This script gently handles the migration for them.


def migrate_datalayers(apps, schema_editor):
    DataLayer = apps.get_model("umap", "DataLayer")

    datalayers = DataLayer.objects.filter(
        settings__remoteData__url__icontains="datalayer"
    )

    for item in datalayers:
        old_url = item.settings["remoteData"]["url"]
        match = re.search(
            rf"{settings.SITE_URL}/datalayer/(?P<map_id>\d+)/(?P<datalayer_id>\d+)",
            old_url,
        )
        if match:
            remote_id = match.group("datalayer_id")
            map_id = match.group("map_id")
            try:
                remote_uuid = DataLayer.objects.get(id=remote_id).uuid
            except DataLayer.DoesNotExist:
                pass
            else:
                try:
                    new_url = settings.SITE_URL + reverse(
                        "datalayer_view", args=[map_id, remote_uuid]
                    )
                except NoReverseMatch:
                    pass
                else:
                    item.settings["remoteData"]["url"] = new_url
                    item.save()


class Migration(migrations.Migration):
    dependencies = [
        ("umap", "0018_datalayer_uuid"),
    ]

    operations = [
        migrations.RunPython(migrate_datalayers, reverse_code=migrations.RunPython.noop)
    ]
