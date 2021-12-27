from .common import (TestPayrollHolidaysHistoryBase)


class TestPayrollHolidaySetting(TestPayrollHolidaysHistoryBase):

    def setUp(self):
        super(TestPayrollHolidaySetting, self).setUp()

    def test_set_values(self):
        settings = self.env['res.config.settings'].create({})
        settings.set_values()
