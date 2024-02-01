import sys
from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from ui_modules.ExpenseTracker_ui import *
from ui_modules.add_a_purchase_ui import *
from PyQt5.QtCore import *

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import plotly.express as px
import pandas as pd
import sqlite3
###################### Expense Tracker ######################
###################### Noor Elyass ######################
###################### January 29th, 2020 ######################

#   MAIN DIALOG

class DlgMain(QDialog, Ui_dlgExpenseTracker):
    def __init__(self):
        super(DlgMain, self).__init__()
        self.setWindowTitle("Expense Tracker")

        self.setupUi(self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        self.lytMain.addWidget(self.browser)

        self.setLayout(self.lytMain)

        self.lytMain.setStretch(0,1)
        self.lytMain.setStretch(1,8)

        self.tblPurchases.setColumnWidth(0, 50)
        self.tblPurchases.setColumnWidth(1, 175)
        self.tblPurchases.setColumnWidth(2, 110)
        self.tblPurchases.setColumnWidth(3, 120)
        self.tblPurchases.setColumnWidth(4, 140)

        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("data/expenses.db")

        if db.open():
            print(db.tables())
            if "purchase" not in db.tables():
                self.createExpenseTable()
            self.populateTable()
        else:
            QMessageBox.critical(self, "Connection Error", "Error connecting to the database.")

        self.btnAdd.clicked.connect(self.evt_btnAdd_clicked)
        self.btnUpdate.clicked.connect(self.evt_btnUpdate_clicked)
        self.btnDelete.clicked.connect(self.evt_btnDelete_clicked)

        self.btnAnalysis.clicked.connect(self.evt_btnAnalysis_clicked)

# The following function, populateTable, details how the table should be filled by the database. To communicate with Sqlite3, commands are written as strings.
# If the query command was executed, the program can now fill the table. It clears it every time so the rows don't duplicate.
# Also, the column headings are created here.
    def populateTable(self):
        query = QSqlQuery()
        bOk = query.exec("SELECT * FROM purchase")
        if bOk:
            self.tblPurchases.clear()
            self.tblPurchases.setRowCount(0)
            self.tblPurchases.setColumnCount(5)
            self.tblPurchases.setHorizontalHeaderLabels(["ID", "Purchase", "Cost", "Category", "When?"])
            while query.next():
                if query.isValid():
                    row = self.tblPurchases.rowCount()
                    self.tblPurchases.insertRow(row)
                    for col in range(5):
                        twi = QTableWidgetItem(str(query.value(col)))
                        self.tblPurchases.setItem(row, col, twi)
        else:
            QMessageBox.critical(self, "Database Error", "Errorx executing query.")

# The following function, returnPurchase, returns the row associated with the id provided in the argument.
# This becomes helpful later, when we use the row to reference the id (see evt_btnUpdate_clicked)
    def returnPurchase(self, id):
        query = QSqlQuery()
        bOk = query.exec("SELECT * FROM purchase WHERE purchase_id = {}".format(id))
        if bOk:
            query.next()
            if query.isValid():
                return query
            else:
                return None
        else: QMessageBox.warning(self, "Database Error", "Database error\n\n{}".format(query.lastError()))

# This function details what happens when btnAdd (add purchase button) is clicked.
# It also sets the date/time to the current date and time.
# It connects the click signal of the button to the event handler (slot).
    def evt_btnAdd_clicked(self):
        dlgAdd = DlgAdd()
        dlgAdd.dteWhen.setCalendarPopup(True)
        dlgAdd.dteWhen.setDateTime(QDateTime.currentDateTime())
        dlgAdd.btnAdd.clicked.connect(dlgAdd.evt_btnAdd_clicked)
        dlgAdd.show()
        dlgAdd.exec_()
        self.populateTable()

# This function details what happens when btnUpdate (update purchase button) is clicked.
# Opposite of returnPurchase, it returns the id associated with the row of a selected item (twi).
# It still uses the original Add Purchase dialog, but alters it so that the heading and button is appropriate and the values
# are pre-entered so they are ready to be edited.
# The data is re-entered into the database.
# It connects the click signal of the button to the event handler (slot).
    def evt_btnUpdate_clicked(self):
        selected_twis = self.tblPurchases.selectedItems()

        if selected_twis:
            selected_twi = selected_twis[0]
            row_twi = selected_twi.row()
            twi_id = self.tblPurchases.item(row_twi, 0)
            id = twi_id.data(0)

            dlgUpdate = DlgAdd()
            dlgUpdate.setWindowTitle("Update Existing Record")
            dlgUpdate.lblTitle.setText("UPDATE A PURCHASE")
            dlgUpdate.btnAdd.setText("Update Purchase")
            selected_purchase = self.returnPurchase(id)
            dlgUpdate.ledID.setText(str(id))
            dlgUpdate.ledPurchase.setText(selected_purchase.value('purchase'))
            dlgUpdate.dsbCost.setValue(selected_purchase.value('cost'))
            dlgUpdate.cmbCategory.setCurrentText(selected_purchase.value('category'))
            dlgUpdate.dteWhen.setCalendarPopup(True)
            dlgUpdate.dteWhen.setDateTime(QDateTime.fromString(selected_purchase.value('purchase_date')))
            dlgUpdate.btnAdd.clicked.connect(dlgUpdate.evt_btnUpdate_clicked)
            dlgUpdate.show()
            dlgUpdate.exec()
            self.populateTable()
        else:
            QMessageBox.warning(self, "Warning", "No purchase selected\n\nPlease select a purchase and try again.")

# This function details what happens when btnDelete (delete purchase button) is clicked.
# Also finds the id using the row of the selected item, but instead of updating purposes, uses this to delete the record.
# It connects the click signal of the button to the event handler (slot).
    def evt_btnDelete_clicked(self):
        selected_twis = self.tblPurchases.selectedItems()

        if selected_twis:
            selected_twi = selected_twis[0]
            row_twi = selected_twi.row()
            twi_id = self.tblPurchases.item(row_twi, 0)
            id = twi_id.data(0)
            res = QMessageBox.question(self, "Delete", "Are you sure you want to delete this selection?")
            if res == QMessageBox.Yes:
                query = QSqlQuery()
                Sql = "DELETE FROM purchase WHERE purchase_id = {}".format(id)
                bOk = query.exec(Sql)
                if bOk:
                    QMessageBox.information(self, "Success!", "You have successfully deleted the purchase.")
                else:
                    QMessageBox.warning(self, "Database Error", "Database error\n\n{}".format(query.lastError().text()))
                self.populateTable()
        else:
            QMessageBox.warning(self, "Warning", "No purchase selected\n\nPlease select a purchase and try again.")

# This function details what happens when the Analysis button is clicked.
# Opens new dialog with two buttons: one is a pie chart showing spending in different categories, the other
# is a bar graph showing spending on different days of the week.
    def evt_btnAnalysis_clicked(self):
        dlgAnalysis = DlgAnalysis()
        dlgAnalysis.btnPieCategory.clicked.connect(dlgAnalysis.evt_btnPieCategory_clicked)
        dlgAnalysis.btnBarDay.clicked.connect(dlgAnalysis.evt_btnBarDay_clicked)
        dlgAnalysis.show()
        dlgAnalysis.exec_()
        # self.populateTable()

# This function creates an empty purchase table in the Sqlite3 database.
    def createExpenseTable(self):
        sql = ''' CREATE TABLE IF NOT EXISTS purchase (
                purchase_id INTEGER PRIMARY KEY,
                purchase TEXT NOT NULL,
                cost REAL NOT NULL,
                category TEXT NOT NULL,
                purchase_date TEXT NOT NULL)'''

        query = QSqlQuery()
        query.exec(sql)
        query.exec("INSERT INTO purchase VALUES (1,'Apple',2.00,'Grocery','Mon Jan 25 17:40:30 2020' )")

#       ADD A PURCHASE DIALOG

class DlgAdd(QDialog, Ui_dlgAdd):
    def __init__(self):
        super(DlgAdd, self).__init__()
        self.setupUi(self)
        self.btnAdd.setFocus()
        self.ledID.setAlignment(QtCore.Qt.AlignRight)

        if not QSqlDatabase.connectionNames():
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName("data/expenses.db")

# The below line populates the led widget with the next available ID, using getId.
        self.ledID.setText(str(self.getId()))
# This line populates the combo box (drop down menu) with the possible categories.
        self.cmbCategory.addItems(['Grocery', 'Fast Food', 'Clothes', 'Subscriptions', 'Transportation', 'Personal Care'])

# This function determines the next available ID by finding the maximum ID so far, and adding 1 to it.
# If table is empty, then the function returns 1.
    def getId(self):
        query = QSqlQuery()
        query.exec("SELECT max(purchase_id) AS max FROM purchase")
        query.next()
        if query.isValid():
            if query.value('max'):
                return query.value('max') + 1
            else:
                return 1

# This function adds a new purchase record to the database.
    def evt_btnAdd_clicked(self):
        query = QSqlQuery()
        query.prepare("INSERT into purchase ('purchase_id', 'purchase', 'cost', 'category', 'purchase_date') VALUES(:id, :pur, :cst, :cat, :dt)")
        query.bindValue(":id", self.ledID.text())
        query.bindValue(":pur", self.ledPurchase.text())
        query.bindValue(":cst", self.dsbCost.value())
        query.bindValue(":cat", str(self.cmbCategory.currentText()))
        query.bindValue(":dt", self.dteWhen.dateTime().toString())
        bOk = query.exec()
        if bOk:
            QMessageBox.information(self, "Success!", "You have successfully added a purchase.")
            self.close()
        else:
            QMessageBox.warning(self, "Database Error", "Database error\n\n{}".format(query.lastError().text()))

# This function updates the selected record in the database.
    def evt_btnUpdate_clicked(self):
        query = QSqlQuery()

        query.prepare("UPDATE purchase SET purchase=:pur, cost=:cst, category=:cat, purchase_date=:dt WHERE purchase_id=:id")
        query.bindValue(":id", self.ledID.text())
        query.bindValue(":pur", self.ledPurchase.text())
        query.bindValue(":cst", self.dsbCost.value())
        query.bindValue(":cat", str(self.cmbCategory.currentText()))
        query.bindValue(":dt", self.dteWhen.dateTime().toString())
        bOk = query.exec()
        if bOk:
            QMessageBox.information(self, "Success!", "You have successfully updated a purchase.")
            self.close()
        else:
            QMessageBox.warning(self, "Database Error", "Database error\n\n{}".format(query.lastError().text()))

#           ANALYSIS DIALOG
class DlgAnalysis(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.btnPieCategory = QPushButton('Category Breakdown', self)
        self.btnBarDay = QPushButton('Typical Week of Spending', self)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.btnPieCategory, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.btnBarDay, alignment=QtCore.Qt.AlignHCenter)
        vlayout.addWidget(self.browser)

        self.resize(1000,800)

# Selected columns from the purchase table in the database are converted into a dataframe so that graphs can be made.
        con = sqlite3.connect("data/expenses.db")
        self.df = pd.read_sql_query("SELECT cost, category, substr(purchase_date,1,3) AS 'Purchase Day' from purchase", con)
        con.close()

# This function details what happens when the Pie Chart button of the analysis dialog is clicked.
# Creates a pie chart figure.
    def evt_btnPieCategory_clicked(self):
        fig = px.pie(self.df, values='cost', names='category')
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

# This function details what happens when the bar graph button of the analysis dialog is clicked.
# Creates a bar graph figure.
    def evt_btnBarDay_clicked(self):
        fig = px.bar(self.df, x='Purchase Day', y='cost')
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlgMain = DlgMain()
    dlgMain.show()
    sys.exit(app.exec_())
