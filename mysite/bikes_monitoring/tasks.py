from mysite.celery import app
from celery.schedules import schedule
from datetime import datetime
# from bikes_monitoring.PrestaRequest.mainp.db.db_writer import ReserveBikes
from bikes_monitoring.PrestaRequest.mainp.reserver import Reserve


@app.task
def auto_delete_reserve(comb_id, phone_number, request_url, api_key):
    # rb = ReserveBikes()
    # rb.deactivate_reservation(comb_id=comb_id, phone_number=phone_number)
    rb = Reserve(api_secret_key=api_key, request_url=request_url)
    db_data = {}
    db_data["comb_id"] = comb_id
    db_data["phone_number"]=phone_number

    rb.db_data = db_data
    rb.url_to_delete = request_url

    rb.deactivate()


    return True