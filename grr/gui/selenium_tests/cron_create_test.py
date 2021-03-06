#!/usr/bin/env python
# -*- mode: python; encoding: utf-8 -*-
"""Test the cron creation UI."""


import unittest
from grr.gui import gui_test_lib
from grr.lib import flags
from grr.lib import output_plugin
from grr.lib.flows.general import processes
from grr.lib.hunts import standard


class DummyOutputPlugin(output_plugin.OutputPlugin):
  """Output plugin that takes processes.ListProcessesArgs and does nothing."""

  name = "dummy"
  description = "Dummy do do."
  args_type = processes.ListProcessesArgs

  def ProcessResponses(self, responses):
    pass


class TestCronView(gui_test_lib.GRRSeleniumTest):
  """Test the Cron view GUI."""

  def testHuntSchedulingWorksCorrectly(self):
    self.Open("/")
    self.Click("css=a[grrtarget=crons]")

    self.Click("css=button[name=ScheduleHuntCronJob]")
    self.WaitUntil(self.IsTextPresent, "Cron Job properties")

    # Select daily periodicity
    self.Type("css=grr-new-cron-job-wizard-form "
              "label:contains('Periodicity') ~ * input", "1d")

    # Click on "Next" button
    self.Click("css=grr-new-cron-job-wizard-form button.Next")

    self.WaitUntil(self.IsTextPresent, "What to run?")

    # Click on Filesystem item in flows list
    self.WaitUntil(self.IsElementPresent, "css=#_Filesystem > i.jstree-icon")
    self.Click("css=#_Filesystem > i.jstree-icon")

    # Click on Find Files item in Filesystem flows list
    self.Click("link=File Finder")

    # Change "path" and "pathtype" values
    self.Type("css=grr-new-cron-job-wizard-form "
              "grr-form-proto-repeated-field:has(label:contains('Paths')) "
              "input", "/tmp")
    self.Select("css=grr-new-cron-job-wizard-form "
                "grr-form-proto-single-field:has(label:contains('Pathtype')) "
                "select", "TSK")

    # Click on "Next" button
    self.Click("css=grr-new-cron-job-wizard-form button.Next")
    self.WaitUntil(self.IsTextPresent, "Output Processing")

    # Configure the hunt to use dummy output plugin.
    self.Click("css=grr-new-cron-job-wizard-form button[name=Add]")
    self.Select("css=grr-new-cron-job-wizard-form select", "DummyOutputPlugin")
    self.Type(
        "css=grr-new-cron-job-wizard-form "
        "grr-form-proto-single-field:has(label:contains('Filename Regex')) "
        "input", "some regex")

    # Click on "Next" button
    self.Click("css=.Wizard button.Next")
    self.WaitUntil(self.IsTextPresent, "Where to run?")

    # Create 3 foreman rules. Note that "Add" button adds rules to the beginning
    # of a list.
    self.Click("css=grr-new-cron-job-wizard-form button[name=Add]")
    self.Select("css=grr-new-cron-job-wizard-form div.well select", "Regex")
    self.Select("css=grr-new-cron-job-wizard-form div.well "
                "label:contains('Attribute name') ~ * select", "System")
    self.Type("css=grr-new-cron-job-wizard-form div.well "
              "label:contains('Attribute regex') ~ * input", "Linux")

    self.Click("css=grr-new-cron-job-wizard-form button[name=Add]")
    self.Select("css=grr-new-cron-job-wizard-form div.well select", "Integer")
    self.Select("css=grr-new-cron-job-wizard-form div.well "
                "label:contains('Attribute name') ~ * select", "Clock")
    self.Select("css=grr-new-cron-job-wizard-form div.well "
                "label:contains('Operator') ~ * select", "GREATER_THAN")
    self.Type("css=grr-new-cron-job-wizard-form div.well "
              "label:contains('Value') ~ * input", "1336650631137737")

    self.Click("css=grr-new-cron-job-wizard-form button[name=Add]")
    self.Click("css=grr-new-cron-job-wizard-form div.well "
               "label:contains('Os darwin') ~ * input[type=checkbox]")

    # Click on "Next" button
    self.Click("css=grr-new-cron-job-wizard-form button.Next")
    self.WaitUntil(self.IsTextPresent, "Review")

    # Check that the arguments summary is present.
    self.assertTrue(self.IsTextPresent("Paths"))
    self.assertTrue(self.IsTextPresent("/tmp"))

    # Check that output plugins are shown.
    self.assertTrue(self.IsTextPresent("DummyOutputPlugin"))

    # Check that rules summary is present.
    self.assertTrue(self.IsTextPresent("Client rule set"))

    # Check that periodicity information is present in the review.
    self.assertTrue(self.IsTextPresent("Periodicity"))
    self.assertTrue(self.IsTextPresent("1d"))

    # Click on "Schedule" button
    self.Click("css=grr-new-cron-job-wizard-form button.Next")

    # Anyone can schedule a hunt but we need an approval to actually start it.
    self.WaitUntil(self.IsTextPresent, "Created Cron Job:")

    # Close the window and check that cron job object was created.
    self.Click("css=grr-new-cron-job-wizard-form button.Next")

    # Select newly created cron job.
    self.Click("css=td:contains('CreateAndRunGenericHuntFlow_')")

    # Check that correct details are displayed in cron job details tab.
    self.WaitUntil(self.IsTextPresent,
                   standard.CreateAndRunGenericHuntFlow.__name__)
    self.WaitUntil(self.IsTextPresent, "Flow Arguments")

    self.assertTrue(self.IsTextPresent("Paths"))
    self.assertTrue(self.IsTextPresent("/tmp"))


def main(argv):
  # Run the full test suite
  unittest.main(argv)


if __name__ == "__main__":
  flags.StartMain(main)
