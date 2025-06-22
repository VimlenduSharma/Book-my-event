<%text>
# ——————————————————————————————————————————————————————————————
# Auto-generated Alembic migration script
# (Template adjusted for cleaner output)
# ——————————————————————————————————————————————————————————————
# revision identifiers, used by Alembic.
revision = ${up_revision!r}
down_revision = ${down_revision!r}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}
# ——————————————————————————————————————————————————————————————
</%text>

from alembic import op
import sqlalchemy as sa

${imports if imports else ""}

def upgrade() -> None:
${indent("\n".join(upgrades), "    ") or "    pass"}

def downgrade() -> None:
${indent("\n".join(downgrades), "    ") or "    pass"}
