from utils.utils_test import Utils


class Test_Components:
    """
    This test include the component testing that
    help us to test the answer from the client
    """
    def test_get_booking_ok(self, client, db):
        Utils.insert_reservation()
        response = client.get("/book/1", follow_redirects=True)
        assert response.status_code == 200
        assert response.json["id"] == 1

        Utils.delete_all_reservations()

    def test_get_booking__with_dates_ok(self, client, db):
        Utils.insert_reservation()
        response = client.get("/book/1?fromDate=2021-04-27T12:00:00Z?toDate=2021-04-27T13:00:00Z", follow_redirects=True)
        assert response.status_code == 200
        assert response.json["id"] == 1

        Utils.delete_all_reservations()

    def test_get_booking_ko(self, client, db):

        response = client.get("/book/1", follow_redirects=True)
        assert response.status_code == 404

    def test_delete_booking_ok(self, client, db):
        reservation = Utils.insert_reservation()
        response = client.delete("/book/{}?user_id={}".format(reservation.id, reservation.customer_id), follow_redirects=True)
        assert response.status_code == 200

        Utils.delete_all_reservations()

    def test_delete_booking_ko(self, client, db):
        response = client.delete("/book/1?user_id=1", follow_redirects=True)
        assert response.status_code == 404

    def test_checkin_ok(self, client, db):
        reservation = Utils.insert_reservation()
        response = client.get("/book/{}/checkin".format(reservation.id, follow_redirects=True))
        assert response.status_code == 200
        Utils.delete_all_reservations()

    def test_checkin_ko(self, client, db):
        reservation = Utils.insert_reservation()

        response = client.get("/book/{}/checkin".format(reservation.id + 1, follow_redirects=True))
        assert response.status_code == 404
        Utils.delete_all_reservations()
