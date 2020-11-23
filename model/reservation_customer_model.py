from model.table_model import TableModel
from model.user_model import UserModel


class ReservationCustomerModel:

    def fill_from_Reservation(self, reservation):
        self.checkin = reservation.checkin
        self.id = reservation.id
        self.people_number = reservation.people_number
        self.reservation_date = reservation.reservation_date
        self.reservation_end = reservation.reservation_end

    def addTable(self, table):
        table_model = TableModel()
        table_model.fill_from_json(table)
        self.table = table_model

    def addCustomer(self, customer):
        self.customer = customer
