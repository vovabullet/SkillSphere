import logging

from prometheus_client.core import GaugeMetricFamily

logger = logging.getLogger(__name__)


class ResumeProfessionCollector:
    """Custom Prometheus collector that reads resume counts per profession from the DB."""

    def collect(self):
        from app import db
        from app.models.resume import Resume
        from sqlalchemy import func

        gauge = GaugeMetricFamily(
            'resume_by_profession_total',
            'Total number of resumes per profession (based on resume title)',
            labels=['profession'],
        )

        try:
            results = (
                db.session.query(Resume.title, func.count(Resume.id).label('count'))
                .group_by(Resume.title)
                .all()
            )
            for title, count in results:
                if title:
                    gauge.add_metric([title], count)
        except Exception:
            logger.exception('Failed to collect resume profession metrics from database')

        yield gauge
