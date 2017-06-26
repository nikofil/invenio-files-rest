#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Create ObjectVersionTag model."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b424b7c75aab'
down_revision = '2e97565eba72'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    if op.get_context().dialect.name == 'postgresql':
        op.execute('ALTER TABLE files_object DROP CONSTRAINT pk_files_object;')
    else:
        op.execute('ALTER TABLE files_object DROP PRIMARY KEY;')
    op.execute('ALTER TABLE files_object ADD PRIMARY KEY (version_id)');
    op.create_table('files_objecttags',
                    sa.Column('version_id',
                              sqlalchemy_utils.types.uuid.UUIDType(),
                              nullable=False),
                    sa.Column('key', sa.String(length=255), nullable=False),
                    sa.Column('value', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['version_id'],
                                            [u'files_object.version_id'],
                                            name=op.f(
                        'fk_files_objecttags_version_id_files_object'),
                        ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('version_id', 'key',
                                            name=op.f('pk_files_objecttags'))
                    )
    op.alter_column(u'files_object', 'bucket_id',
                    existing_type=sqlalchemy_utils.types.uuid.UUIDType(),
                    nullable=True)
    op.alter_column(u'files_object', 'key',
                    existing_type=sa.Text().with_variant(mysql.VARCHAR(255),
                                                         'mysql'),
                    nullable=True)
    op.create_unique_constraint(op.f('uq_files_object_bucket_id'),
                                'files_object', ['version_id'])
    # ### end Alembic commands ###


def downgrade():
    """Downgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    if op.get_context().dialect.name == 'postgresql':
        op.execute('ALTER TABLE files_object DROP CONSTRAINT pk_files_object;')
    else:
        op.execute('ALTER TABLE files_object DROP PRIMARY KEY;')
    op.execute('ALTER TABLE files_object ADD PRIMARY KEY '
               '(bucket_id, key, version_id);')
    op.drop_constraint(op.f('uq_files_object_bucket_id'),
                       'files_object', type_='unique')
    op.alter_column(u'files_object', 'key',
                    existing_type=sa.Text().with_variant(mysql.VARCHAR(255),
                                                         'mysql'),
                    nullable=False)
    op.alter_column(u'files_object', 'bucket_id',
                    existing_type=sqlalchemy_utils.types.uuid.UUIDType(),
                    nullable=False)
    op.drop_table('files_objecttags')
    # ### end Alembic commands ###