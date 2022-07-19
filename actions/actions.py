# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from asyncore import dispatcher
from dis import dis
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_core_sdk.forms import FormAction
from rasa_sdk.events import SlotSet

import numpy as np
import pandas as pd
import re
import string
import random
import uuid
from datetime import datetime

from . import utils_chatbot as u

class ValidateAddResourcesForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_add_resources_form"

    @staticmethod
    def add_resource_time_table_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_timetables = u.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def add_resource_new_role_db() -> List[Text]:
        """Database of supported roles for new role."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_tasks = u.extract_tasks(model_path)

        return list(df_tasks['taskName'])

    @staticmethod
    def add_resource_name_db() -> List[Text]:
        """Database of supported roles for new role."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_add_resource_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        resources = self.add_resource_name_db()

        if value.lower() not in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_name": value}
        else:
            dispatcher.utter_message('\n'.join(resources))
            dispatcher.utter_message(response="utter_wrong_add_resource_name")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_name": None}

    def validate_add_resource_time_table(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_time_table value."""

        timetables = self.add_resource_time_table_db()

        if value.lower() in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_time_table": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_time_table")
            dispatcher.utter_message('\n'.join(timetables))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_time_table": None}

    def validate_add_resource_new_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_new_role value."""

        tasks = self.add_resource_new_role_db()
        
        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"add_resource_new_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_new_role")
            dispatcher.utter_message('\n'.join(tasks))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"add_resource_new_role": None}

    def validate_add_resource_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_amount value."""

        if self.is_int(value) and int(value) > 0:
            return {"add_resource_amount": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_amount")
            # validation failed, set slot to None
            return {"add_resource_amount": None}

    def validate_add_resource_cost(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_cost value."""

        if self.is_int(value) and int(value) > 0:
            return {"add_resource_cost": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_cost")
            # validation failed, set slot to None
            return {"add_resource_cost": None}

class AddResourcesForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "add_resources_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["add_resource_name", "add_resource_amount", "add_resource_cost",
                "add_resource_time_table", "add_resource_new_role"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionAddResource(Action):
    def name(self) -> Text:
        return "action_add_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)
        df_timetables = u.extract_timetables(model_path)
        
        resourceId = 'qbp_{}'.format(uuid.uuid4())
        resourceName = tracker.get_slot("add_resource_name")
        totalAmount = tracker.get_slot("add_resource_amount")
        costPerHour = tracker.get_slot("add_resource_cost")
        
        timetableName = tracker.get_slots("add_resource_time_table")
                
        timetableId = df_timetables[df_timetables['timetableName']== timetableName]['timetableId']
        
        df_new_role = pd.DataFrame([{'resourceId':resourceId, 'resourceName':resourceName, 'totalAmount':totalAmount, \
                            'costPerHour':costPerHour, 'timetableId':timetableId}])
        df_resources = pd.concat([df_resources, df_new_role])
        
        df_elements = u.extract_elements(model_path)
        df_tasks = u.extract_tasks(model_path)
        df_tasks_elements = df_tasks.merge(df_elements, how='left', on='elementId')
        df = df_tasks_elements[['taskName', 'elementId', 'resourceId']].merge(df_resources, how='left', on='resourceId')
        
        df_transformed = df.copy()

        task_new_role = tracker.get_slot("add_resource_new_role")
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'resourceId'] = resourceId
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'resourceName'] = resourceName
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'totalAmount'] = totalAmount
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'costPerHour'] = costPerHour
        df_transformed.loc[df_transformed['taskName'].str.lower() == task_new_role.lower(), 'timetableId'] = timetableId
        
        ptt_s = '<qbp:elements>'
        ptt_e = '</qbp:elements>'
        elements = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        element_lines = elements.split('\n')
        elements_list = []
        start, end = None, None
        for idx, line in enumerate(element_lines):
            if '<qbp:element ' in line and start == None:
                start = idx
            if '</qbp:element>' in line and end == None:
                end = idx
            if start != None and end != None:
                elements_list.append('\n'.join(element_lines[start:end+1]))
                start, end = None, None
                
        df = df.sort_values(by='taskName')
        df_transformed = df_transformed.sort_values(by='taskName')
        
        # Extract new elements and replace old one with new elements extracted
        new_elements = []
        for i in range(len(elements_list)):
            element = elements_list[i]
            old_elem = list(df[df['taskName'].str.lower() == task_new_role.lower()]['resourceId'])[0]
            new_elem = list(df_transformed[df_transformed['taskName'].str.lower() == task_new_role.lower()]['resourceId'])[0]
            if 'elementId="{}"'.format(list(df[df['taskName'].str.lower() == task_new_role.lower()]['elementId'])[0]) in element:
                new_element = element.replace(old_elem, new_elem)
                new_elements.append(new_element)
        
        new_elements = '\n'.join([element_lines[0]] + new_elements + [element_lines[-1]])
        
        with open(model_path) as file:
            model= file.read()
        new_model = model.replace(elements, new_elements)        
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources = u.extract_bpmn_resources(model_path, ptt_s, ptt_e).split('\n')
        new_res = '      <qbp:resource id="{}" name="{}" totalAmount="{}" costPerHour="{}" timetableId="{}"/>'.format(resourceId, resourceName, totalAmount, \
                                                                                                                costPerHour, timetableId)
        new_resources = '\n'.join(resources[:-1] + [new_res] + [resources[-1]])
        new_model = new_model.replace('\n'.join(resources), new_resources)
        
        new_model_path = model_path.split('.')[0] + '_add_resource_{}'.format(resourceName.replace(' ', '_')) + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/resources/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_add_resource_{}.csv'.format(resourceName.replace(' ', '_'))
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, 'Addition of resource {}'.format(resourceName))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')
            
        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        
        return []

class ActionIncreaseDemand(Action):
    """
    Action for increase demand
    """

    def name(self) -> Text:
        return "action_increase_demand"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        input_m = next(tracker.get_latest_entity_values("inc_percentage"))
        inc_percentage = float(input_m)
        percentage = inc_percentage/100 if inc_percentage > 1 else inc_percentage 

        new_model_path = u.modify_bimp_model_instances(model_path, percentage)
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/demand/output_inc_demand_{}.csv'.format(int(percentage*100))
       
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)

        output_message = u.return_message_stats(csv_output_path, 'Increased demand in {} percent'.format(int(100*percentage)))

        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/demand/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(output_message)
        return []

class ActionDecreaseDemand(Action):
    """
    Action for decrease demand
    """

    def name(self) -> Text:
        return "action_decrease_demand"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        input_m = next(tracker.get_latest_entity_values("dec_percentage"), None)
        dec_percentage = float(input_m)
        percentage = dec_percentage/100 if np.abs(dec_percentage) > 1 else dec_percentage
            
        new_model_path = u.modify_bimp_model_instances(model_path, percentage)

        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/demand/output_dec_demand_{}.csv'.format(int(np.abs(percentage)*100))
        
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)

        output_message = u.return_message_stats(csv_output_path, 'Decreased demand in {} percent'.format(int(100*np.abs(percentage))))

        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/demand/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(output_message)
        return []

class ValidateChangeResourcesForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_change_resources_form"

    @staticmethod
    def change_resources_role_modify_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_change_resources_role_modify(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        resources = self.change_resources_role_modify_db()

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"change_resources_role_modify": value}
        else:
            dispatcher.utter_message(response="utter_wrong_change_resources_role_modify")
            dispatcher.utter_message('\n'.join(resources))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"change_resources_role_modify": None}

    def validate_change_resource_new_amount(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_resource_new_amount value."""

        if self.is_int(value) and int(value) > 0:
            return {"change_resource_new_amount": value}
        else:
            dispatcher.utter_message(response="utter_wrong_add_resource_amount")
            # validation failed, set slot to None
            return {"change_resource_new_amount": None}

    def validate_change_resource_new_cost(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate change_resource_new_cost value."""

        if self.is_int(value) and int(value) > 0:
            return {"change_resource_new_cost": value}
        else:
            dispatcher.utter_message(response="utter_wrong_change_resource_new_cost")
            # validation failed, set slot to None
            return {"change_resource_new_cost": None}

class ChangeResourcesForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "change_resources_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["change_resources_role_modify", "change_resource_new_amount", "change_resource_new_cost"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionChangeResource(Action):
    def name(self) -> Text:
        return "action_change_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        df_resources = u.extract_resources(model_path)
        
        mod_res = tracker.get_slot("change_resources_role_modify")
        amount = df_resources[df_resources['resourceName']==mod_res]['totalAmount'].values[0]
        cost = df_resources[df_resources['resourceName']==mod_res]['costPerHour'].values[0]
        
        new_amount = tracker.get_slot("change_resources_new_amount")
        new_cost = tracker.get_slot("change_resources_new_cost")
        
        df_resources.loc[df_resources['resourceName']==mod_res, ['totalAmount']] = new_amount
        df_resources.loc[df_resources['resourceName']==mod_res, ['costPerHour']] = new_cost
        
        mod_name = mod_res.replace(' ', '_')
        new_model_path = u.modify_bimp_model_resources(model_path, amount, new_amount, cost, new_cost)
        
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_mod_resource_{}.csv'.format(mod_name)
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, 'Modification of resource {}'.format(mod_name))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)

        return []

class ValidateFastTaskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_fast_task_form"

    @staticmethod
    def fast_task_name_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_tasks, task_dist = u.extract_task_add_info(model_path)

        return list(df_tasks['name'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_fast_task_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        tasks = self.fast_task_name_db()

        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"fast_task_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_fast_task_name")
            dispatcher.utter_message('\n'.join(tasks))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"fast_task_name": None}

    def validate_fast_task_percentage(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate fast_task_percentage value."""

        if self.is_int(value) and int(value) > 0 and int(value) < 100:
            return {"fast_task_percentage": value}
        else:
            dispatcher.utter_message(response="utter_wrong_fast_task_percentage")
            # validation failed, set slot to None
            return {"fast_task_percentage": None}

class FastTaskForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "fast_task_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["fast_task_name", "fast_task_percentage"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionFastTask(Action):
    def name(self) -> Text:
        return "action_fast_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        df_tasks, task_dist = u.extract_task_add_info(model_path)
        
        task = tracker.get_slot("fast_task_name")
        percentage = int(tracker.get_slot("fast_task_percentage"))/100

        df_tasks.loc[df_tasks['name'].str.lower() == task.lower(), ['mean']] = (1-percentage)*int(df_tasks[df_tasks['name'].str.lower() == task.lower()]['mean'].values[0])

        elements = """
            <qbp:elements>
                {}
            </qbp:elements>
        """
        
        element = """      <qbp:element id="{}" elementId="{}">
                <qbp:durationDistribution type="{}" mean="{}" arg1="{}" arg2="{}">
                <qbp:timeUnit>{}</qbp:timeUnit>
                </qbp:durationDistribution>
                <qbp:resourceIds>
                <qbp:resourceId>{}</qbp:resourceId>
                </qbp:resourceIds>
            </qbp:element>
        """
        
        df_tasks['element'] = df_tasks.apply(lambda x: element.format(x['id'], x['elementId'], x['type'], x['mean'], \
                                                                    x['arg1'], x['arg2'], x['timeUnit'], x['resourceId']), \
                                            axis= 1)
            
        new_elements = elements.format("""""".join(df_tasks['element']))
        
        with open(model_path) as file:
            model= file.read()

        new_model = model.replace('\n'.join(task_dist[0]), new_elements)
        sce_name = '_{}_faster_{}'.format(percentage, task)
        
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/fast_slow_task/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/fast_slow_task/output_{}.csv'.format(sce_name)
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, '{}'.format(' '.join(sce_name.split('_'))))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/fast_slow_task/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)

        return []

class ValidateSlowTaskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_slow_task_form"

    @staticmethod
    def slow_task_name_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_tasks, _ = u.extract_task_add_info(model_path)

        return list(df_tasks['name'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_slow_task_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate add_resource_name value."""

        tasks = self.slow_task_name_db()

        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"slow_task_name": value}
        else:
            dispatcher.utter_message(response="utter_wrong_slow_task_name")
            dispatcher.utter_message('\n'.join(tasks))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"slow_task_name": None}

    def validate_slow_task_percentage(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate slow_task_percentage value."""

        if self.is_int(value) and int(value) > 0 and int(value) < 100:
            return {"slow_task_percentage": value}
        else:
            dispatcher.utter_message(response="utter_wrong_slow_task_percentage")
            # validation failed, set slot to None
            return {"slow_task_percentage": None}

class SlowTaskForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "slow_task_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["slow_task_name", "slow_task_percentage"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionSlowTask(Action):
    def name(self) -> Text:
        return "action_slow_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        df_tasks, task_dist = u.extract_task_add_info(model_path)
        
        task = tracker.get_slot("slow_task_name")
        percentage = int(tracker.get_slot("slow_task_percentage"))/100

        df_tasks.loc[df_tasks['name'].str.lower() == task.lower(), ['mean']] = (1+percentage)*int(df_tasks[df_tasks['name'].str.lower() == task.lower()]['mean'].values[0])

        elements = """
            <qbp:elements>
                {}
            </qbp:elements>
        """
        
        element = """      <qbp:element id="{}" elementId="{}">
                <qbp:durationDistribution type="{}" mean="{}" arg1="{}" arg2="{}">
                <qbp:timeUnit>{}</qbp:timeUnit>
                </qbp:durationDistribution>
                <qbp:resourceIds>
                <qbp:resourceId>{}</qbp:resourceId>
                </qbp:resourceIds>
            </qbp:element>
        """
        
        df_tasks['element'] = df_tasks.apply(lambda x: element.format(x['id'], x['elementId'], x['type'], x['mean'], \
                                                                    x['arg1'], x['arg2'], x['timeUnit'], x['resourceId']), \
                                            axis= 1)
            
        new_elements = elements.format("""""".join(df_tasks['element']))
        
        with open(model_path) as file:
            model= file.read()

        new_model = model.replace('\n'.join(task_dist[0]), new_elements)
        sce_name = '_{}_slower_{}'.format(percentage, task)
        
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/fast_slow_task/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/fast_slow_task/output_{}.csv'.format(sce_name)
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, '{}'.format(' '.join(sce_name.split('_'))))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/fast_slow_task/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)

        return []

class ValidateRemoveResourceskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_remove_resources_form"

    @staticmethod
    def remove_resources_role_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)

        return list(df_resources['resourceName'])

    def validate_remove_resources_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate remove_resources_role value."""

        resources = self.remove_resources_role_db()

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"remove_resources_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_remove_resources_role")
            dispatcher.utter_message('\n'.join(resources))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"remove_resources_role": None}

    def validate_remove_resources_transfer_role(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate remove_resources_transfer_role value."""

        resources = self.remove_resources_role_db()

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"remove_resources_transfer_role": value}
        else:
            dispatcher.utter_message(response="utter_wrong_remove_resources_transfer_role")
            dispatcher.utter_message('\n'.join(resources))
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"remove_resources_transfer_role": None}

class RemoveResourcesForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "remove_resources_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["remove_resources_role", "remove_resources_transfer_role"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionRemoveResources(Action):
    def name(self) -> Text:
        return "action_remove_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        df_resources = u.extract_resources(model_path)
        df_timetables = u.extract_timetables(model_path)
        
        res_remove = tracker.get_slot("remove_resources_role")
        new_res_remove = tracker.get_slot("remove_resources_transfer_role")

        df_elements = u.extract_elements(model_path)
        df_tasks = u.extract_tasks(model_path)
        df_tasks_elements = df_tasks.merge(df_elements, how='left', on='elementId')
        df = df_tasks_elements[['taskName', 'elementId', 'resourceId']].merge(df_resources, how='left', on='resourceId')

        resource = df_resources[df_resources['resourceName'] == res_remove][['resourceId', 'resourceName']]
        new_resource = df_resources[df_resources['resourceName'] == new_res_remove ][['resourceId', 'resourceName']]
        
        ptt_s = '<qbp:elements>'
        ptt_e = '</qbp:elements>'
        elements = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        element_lines = elements.split('\n')
        elements_list = []
        start, end = None, None
        for idx, line in enumerate(element_lines):
            if '<qbp:element ' in line and start == None:
                start = idx
            if '</qbp:element>' in line and end == None:
                end = idx
            if start != None and end != None:
                elements_list.append('\n'.join(element_lines[start:end+1]))
                start, end = None, None
                
        # Extract new elements and replace old one with new elements extracted
        new_elements = []
        for i in range(len(elements_list)):
            element = elements_list[i]
            old_e = list(resource['resourceId'])[0]
            new_e = list(new_resource['resourceId'])[0]
            if '<qbp:resourceId>{}</qbp:resourceId>'.format(list(resource['resourceId'])[0]) in element:
                new_element = element.replace(old_e, new_e)
            else:
                new_element = element
            new_elements.append(new_element)
        
        new_elements = '\n'.join([element_lines[0]] + new_elements + [element_lines[-1]])
        with open(model_path) as file:
            model= file.read()
        new_model = model.replace(elements, new_elements) 
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources = u.extract_bpmn_resources(model_path, ptt_s, ptt_e).split('\n')
        new_resources = '\n'.join([x for x in resources if 'name="{}"'.format(list(resource['resourceName'])[0]) not in x])
        new_model = new_model.replace('\n'.join(resources), new_resources)
        
        new_model_path = model_path.split('.')[0] + '_rem_resource_{}'.format(res_remove.replace(' ', '_')) + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/resources/models')
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_rem_resource_{}.csv'.format(res_remove.replace(' ', '_'))
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, 'Remotion of resource {}'.format(res_remove))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/resources/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)

        return []

class ValidateCreateWorkingTimeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_create_working_time_form"

    @staticmethod
    def create_working_time_name_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_timetables = u.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def create_working_time_resource_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def create_working_time_weekday_db() -> List[Text]:
        """Database of supported roles for working times."""

        return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_hour(string: Text) -> bool:
        """Check if a string have hour time format"""
        try:
            datetime.strptime(string, '%H:%M:%S')
            return True
        except:
            return False

    def validate_create_working_time_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_name value."""

        timetables = self.create_working_time_name_db()

        if value.lower() not in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_name": value}
        else:
            dispatcher.utter_message('\n'.join(timetables))
            dispatcher.utter_message(response="utter_wrong_create_working_time_name")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_name": None}

    def validate_create_working_time_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_from_time value."""

        if self.is_hour(value):
            return {"create_working_time_from_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_from_time")
            # validation failed, set slot to None
            return {"create_working_time_from_time": None}

    def validate_create_working_time_resource(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_resource value."""

        resources = self.create_working_time_resource_db()

        if value.lower() in [x.lower() for x in resources]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_resource": value}
        else:
            dispatcher.utter_message('\n'.join(resources))
            dispatcher.utter_message(response="utter_wrong_create_working_time_resource")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_resource": None}

    def validate_create_working_time_to_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_to_time value."""

        if self.is_hour(value):
            return {"create_working_time_to_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_create_working_time_to_time")
            # validation failed, set slot to None
            return {"create_working_time_to_time": None}

    def validate_create_working_time_from_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_from_weekday value."""

        weekdays = self.create_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_from_weekday": value}
        else:
            dispatcher.utter_message('\n'.join(weekdays))
            dispatcher.utter_message(response="utter_wrong_create_working_time_from_weekday")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_from_weekday": None}

    def validate_create_working_time_to_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate create_working_time_to_weekday value."""

        weekdays = self.create_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"create_working_time_to_weekday": value}
        else:
            dispatcher.utter_message('\n'.join(weekdays))
            dispatcher.utter_message(response="utter_wrong_create_working_time_to_weekday")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"create_working_time_to_weekday": None}

class CreateWorkingTimeForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "create_working_time_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["create_working_time_id", "create_working_time_name", "create_working_time_from_time", "create_working_time_to_time", 
        "create_working_time_from_weekday", "create_working_time_to_weekday", "create_working_time_resource"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionCreateWorkingTime(Action):
    def name(self) -> Text:
        return "action_create_working_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
  
        ptt_s = '<qbp:timetables>'
        ptt_e = '</qbp:timetables>'
        time_tables_text = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        time_tables = time_tables_text.split('\n')
        
        data = []
        start = None
        end = None
        for idx, time_table in enumerate(time_tables):
            start = 0
            if '<qbp:timetable ' in time_table and start == None:
                start = idx
            elif '</qbp:timetable>' in time_table and end == None:
                end = idx
                data.append(time_tables[start:end+1])
                start, end = None, None
        
        df_tt = pd.DataFrame(data = [], columns = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        ptts = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay']
        for time_table in data:
            rules = []
            for line in time_table:
                row = {}
                for ptt in ptts:
                    ptt_s = r'{}="(.*?)"'.format(ptt)
                    text = re.search(ptt_s, line)
                    if ptt == 'id' and text != None:
                        id_tt = text.group(1)
                    elif ptt == 'name' and text != None:
                        name_tt = text.group(1)
                    elif text != None:
                        row[ptt] = text.group(1)
                if row != {}:
                    rules.append(row)
            df = pd.DataFrame(rules)
            df['id'] = id_tt
            df['name'] = name_tt
            df = df[ptts]
            df_tt = pd.concat([df_tt, df])

        scenario_name = []
        tt_id = tracker.get_slot("create_working_time_id")
        tt_name = tracker.get_slot("create_working_time_name")

        scenario_name.append('add_{}'.format(tt_name))

        new_tt_rules = []
        from_time = tracker.get_slot("create_working_time_from_time")
        to_time = tracker.get_slot("create_working_time_to_time")
        from_weekday = tracker.get_slot("create_working_time_from_weekday")
        to_weekday = tracker.get_slot("create_working_time_to_weekday")
        rule = [from_time, to_time, from_weekday, to_weekday]
        new_tt_rules.append(rule)

        new_tt_df = pd.DataFrame(new_tt_rules, columns = ['fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        new_tt_df['id'] = tt_id
        new_tt_df['name'] = tt_name

        df_tt = pd.concat([df_tt, new_tt_df[df_tt.columns]])
        
        ptt_s = '<qbp:resources>'
        ptt_e = '</qbp:resources>'
        resources_text = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        resources = resources_text.split('\n')
        
        ptts = ['id', 'name', 'totalAmount', 'costPerHour', 'timetableId']
        data = []
        for line in resources:
            row = {}
            for ptt in ptts:
                ptt_s = r'{}="(.*?)"'.format(ptt)
                text = re.search(ptt_s, line)
                if text != None:
                    row[ptt] = text.group(1)
            if row != {}:
                data.append(row)
                
        df_resources = pd.DataFrame(data)

        res_change_tt = tracker.get_slot("create_working_time_resource")
        df_resources.loc[df_resources['name'] == res_change_tt, 'timetableId'] = tt_id

        format_time_tables = """    <qbp:timetables>{}</qbp:timetables>"""
    
        format_time_table = """\n        <qbp:timetable id="{}" default="false" name="{}">
                <qbp:rules>{}</qbp:rules>
            </qbp:timetable>"""
        
        format_rules_time_tables = """\n            <qbp:rule fromTime="{}" toTime="{}" fromWeekDay="{}" toWeekDay="{}"/>"""
        
        time_tables = list(df_tt['name'].drop_duplicates())
        
        time_tables_updated = []
        for time_table in time_tables:
            df_time_table = df_tt[df_tt['name'] == time_table]
            name_tt = df_time_table['name'].values[0]
            id_tt = df_time_table['id'].values[0]
            df_time_table['rule'] = df_time_table.apply(lambda x: format_rules_time_tables.format(x['fromTime'], x['toTime'], x['fromWeekDay'], x['toWeekDay']), axis= 1)
            rules = """""".join(df_time_table['rule'])
            time_table_tmp = format_time_table.format(id_tt, name_tt, rules)
            time_tables_updated.append(time_table_tmp)
            
        final_time_tables = format_time_tables.format("""""".join(time_tables_updated))

        with open(model_path) as f:
            model = f.read()
            
        new_model = model.replace(time_tables_text, final_time_tables)

        resources = """    <qbp:resources>
          {} 
        </qbp:resources>"""
        
        resource = """<qbp:resource id="{}" name="{}" totalAmount="{}" costPerHour="{}" timetableId="{}"/>"""
        df_resources['resource'] = df_resources.apply(lambda x: resource.format(x['id'], x['name'], x['totalAmount'], \
                                                                                x['costPerHour'], x['timetableId']
                                                                                ), axis=1)
        new_resources = resources.format("""""".join(df_resources['resource']))
        
        new_model = new_model.replace(resources_text, new_resources)
    
        sce_name = ('_' + '_'.join(scenario_name)).replace('/', '_')
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/working_tables/models')
        
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/working_tables/output_{}.csv'.format(sce_name)
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, '{}'.format(' '.join(sce_name.split('_'))))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/working_tables/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        
        return []


class ValidateModifyWorkingTimeForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_modify_working_time_form"

    @staticmethod
    def modify_working_time_name_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_timetables = u.extract_timetables(model_path)

        return list(df_timetables['timetableName'])

    @staticmethod
    def modify_working_time_resource_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_resources = u.extract_resources(model_path)

        return list(df_resources['resourceName'])

    @staticmethod
    def modify_working_time_weekday_db() -> List[Text]:
        """Database of supported roles for working times."""

        return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_hour(string: Text) -> bool:
        """Check if a string have hour time format"""
        try:
            datetime.strptime(string, '%H:%M:%S')
            return True
        except:
            return False

    def validate_modify_working_time_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_name value."""

        timetables = self.modify_working_time_name_db()

        if value.lower() in [x.lower() for x in timetables]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_name": value}
        else:
            dispatcher.utter_message('\n'.join(timetables))
            dispatcher.utter_message(response="utter_wrong_modify_working_time_name")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_name": None}

    def validate_modify_working_time_from_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_from_time value."""

        if self.is_hour(value):
            return {"modify_working_time_from_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_from_time")
            # validation failed, set slot to None
            return {"modify_working_time_from_time": None}

    def validate_modify_working_time_to_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_to_time value."""

        if self.is_hour(value):
            return {"modify_working_time_to_time": value}
        else:
            dispatcher.utter_message(response="utter_wrong_modify_working_time_to_time")
            # validation failed, set slot to None
            return {"modify_working_time_to_time": None}

    def validate_modify_working_time_from_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_from_weekday value."""

        weekdays = self.modify_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_from_weekday": value}
        else:
            dispatcher.utter_message('\n'.join(weekdays))
            dispatcher.utter_message(response="utter_wrong_modify_working_time_from_weekday")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_from_weekday": None}

    def validate_modify_working_time_to_weekday(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate modify_working_time_to_weekday value."""

        weekdays = self.modify_working_time_weekday_db()

        if value.lower() in [x.lower() for x in weekdays]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"modify_working_time_to_weekday": value}
        else:
            dispatcher.utter_message('\n'.join(weekdays))
            dispatcher.utter_message(response="utter_wrong_modify_working_time_to_weekday")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"modify_working_time_to_weekday": None}

class ModifyWorkingTimeForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "modify_working_time_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["modify_working_time_name", "modify_working_time_from_time", "modify_working_time_to_time", 
        "modify_working_time_from_weekday", "modify_working_time_to_weekday"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """

        return []

class ActionModifyWorkingTime(Action):
    def name(self) -> Text:
        return "action_modify_working_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        ptt_s = '<qbp:timetables>'
        ptt_e = '</qbp:timetables>'
        time_tables_text = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)
        time_tables = time_tables_text.split('\n')
        
        data = []
        start = None
        end = None
        for idx, time_table in enumerate(time_tables):
            start = 0
            if '<qbp:timetable ' in time_table and start == None:
                start = idx
            elif '</qbp:timetable>' in time_table and end == None:
                end = idx
                data.append(time_tables[start:end+1])
                start, end = None, None
        
        df_tt = pd.DataFrame(data = [], columns = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        ptts = ['id','name','fromTime', 'toTime', 'fromWeekDay', 'toWeekDay']
        for time_table in data:
            rules = []
            for line in time_table:
                row = {}
                for ptt in ptts:
                    ptt_s = r'{}="(.*?)"'.format(ptt)
                    text = re.search(ptt_s, line)
                    if ptt == 'id' and text != None:
                        id_tt = text.group(1)
                    elif ptt == 'name' and text != None:
                        name_tt = text.group(1)
                    elif text != None:
                        row[ptt] = text.group(1)
                if row != {}:
                    rules.append(row)
            df = pd.DataFrame(rules)
            df['id'] = id_tt
            df['name'] = name_tt
            df = df[ptts]
            df_tt = pd.concat([df_tt, df])


        scenario_name = []
        change_tt_name = tracker.get_slot("modify_working_time_name")
        change_tt_df = df_tt[df_tt['name'].str.lower() == change_tt_name.lower()]
        
        df_tt = df_tt[df_tt['name'] != change_tt_name]
        scenario_name.append('modify_{}'.format(change_tt_name))
        
        tt_id = change_tt_df['id'].drop_duplicates().values[0]
        tt_name = change_tt_df['name'].drop_duplicates().values[0]

        new_tt_rules = []
        from_time = tracker.get_slot("modify_working_time_from_time")
        to_time = tracker.get_slot("modify_working_time_to_time")
        from_weekday = tracker.get_slot("modify_working_time_from_weekday")
        to_weekday = tracker.get_slot("modify_working_time_to_weekday")
        rule = [from_time, to_time, from_weekday, to_weekday]
        new_tt_rules.append(rule)

        new_tt_df = pd.DataFrame(new_tt_rules, columns = ['fromTime', 'toTime', 'fromWeekDay', 'toWeekDay'])
        new_tt_df['id'] = tt_id
        new_tt_df['name'] = tt_name
        df_tt = pd.concat([df_tt, new_tt_df[df_tt.columns]])

        format_time_tables = """    <qbp:timetables>{}</qbp:timetables>"""
    
        format_time_table = """\n        <qbp:timetable id="{}" default="false" name="{}">
                <qbp:rules>{}</qbp:rules>
            </qbp:timetable>"""
        
        format_rules_time_tables = """\n            <qbp:rule fromTime="{}" toTime="{}" fromWeekDay="{}" toWeekDay="{}"/>"""
        
        time_tables = list(df_tt['name'].drop_duplicates())
        
        time_tables_updated = []
        for time_table in time_tables:
            df_time_table = df_tt[df_tt['name'] == time_table]
            name_tt = df_time_table['name'].values[0]
            id_tt = df_time_table['id'].values[0]
            df_time_table['rule'] = df_time_table.apply(lambda x: format_rules_time_tables.format(x['fromTime'], x['toTime'], x['fromWeekDay'], x['toWeekDay']), axis= 1)
            rules = """""".join(df_time_table['rule'])
            time_table_tmp = format_time_table.format(id_tt, name_tt, rules)
            time_tables_updated.append(time_table_tmp)
            
        final_time_tables = format_time_tables.format("""""".join(time_tables_updated))

        with open(model_path) as f:
            model = f.read()
            
        new_model = model.replace(time_tables_text, final_time_tables)

        sce_name = ('_' + '_'.join(scenario_name)).replace('/', '_')
        new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
        new_model_path = new_model_path.replace('inputs','inputs/working_tables/models')
        
        with open(new_model_path, 'w+') as new_file:
            new_file.write(new_model)
            
        csv_output_path = 'C:/CursosMaestria/Tesis/Chatbot/outputs/working_tables/output_{}.csv'.format(sce_name)
        u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
        output_message = u.return_message_stats(csv_output_path, '{}'.format(' '.join(sce_name.split('_'))))
        
        csv_org_path = 'C:/CursosMaestria/Tesis/Chatbot/outputs/working_tables/output_baseline.csv'
        u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
        org_message = u.return_message_stats(csv_org_path, 'Base')

        dispatcher.utter_message(text=org_message)
        dispatcher.utter_message(text=output_message)
        
        return []





class ValidateAutomateTaskForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_automate_task_form"

    @staticmethod
    def automate_task_name_db() -> List[Text]:
        """Database of supported resource timetables."""

        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'
        df_tasks = u.extract_tasks(model_path)

        return list(df_tasks['taskName'])

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_automate_task_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate automate_task_name value."""

        tasks = self.automate_task_name_db()

        if value.lower() in [x.lower() for x in tasks]:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"automate_task_name": value}
        else:
            dispatcher.utter_message('\n'.join(tasks))
            dispatcher.utter_message(response="utter_wrong_automate_task_name")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"automate_task_name": None}

    def validate_automate_task_percentage(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate automate_task_percentage value."""

        if self.is_int(value) and int(value)>0 and int(value)<=100 :
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"automate_task_percentage": value}
        else:
            dispatcher.utter_message(response="utter_wrong_automate_task_percentage")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"automate_task_percentage": None}

   
class AutomateTaskForm(FormAction):

    def name(self):
        """Unique identifier of the form"""
        return "automate_task_form"

    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["automate_task_name","automate_task_percentage"]

    def submit(self):
        """
        Define what the form has to do
        after all required slots are filled
        """
        return []

class ActionAutomateTask(Action):
    def name(self) -> Text:
        return "action_automate_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        bimp_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/bimp/qbp-simulator-engine_with_csv_statistics.jar'
        model_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/inputs/PurchasingExample.bpmn'

        with open(model_path) as file:
            model= file.read()

        df_tasks, _ = u.extract_task_add_info(model_path)

        task = tracker.get_slot("automate_task_name")
        percentage = int(tracker.get_slot("automate_task_percentage"))/100

        df_tasks_new = df_tasks.copy()

        if percentage == 100:
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['type']] = 'UNIFORM'
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']] = 0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['arg1']] = 0.0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['arg2']] = 0.0
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['resourceName']] = 'SYSTEM'
        else:
            df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']] = (1-percentage)*df_tasks_new.loc[df_tasks_new['name'].str.lower() == task.lower(), ['mean']]

            resource_msg = """      <qbp:element id="{}" elementId="{}">
                    <qbp:durationDistribution type="{}" mean="{}" arg1="{}" arg2="{}">
                    <qbp:timeUnit>{}</qbp:timeUnit>
                    </qbp:durationDistribution>
                    <qbp:resourceIds>
                    <qbp:resourceId>{}</qbp:resourceId>
                    </qbp:resourceIds>
                </qbp:element>"""

            elements_new = '\n'.join([resource_msg.format(x['id'], x['elementId'], x['type'], x['mean'], \
                        x['arg1'], x['arg2'], x['timeUnit'], x['resourceId']) for idx, x in df_tasks_new.iterrows()])

            ptt_s = '<qbp:elements>'
            ptt_e = '</qbp:elements>'
            elements_old = u.extract_bpmn_resources(model_path, ptt_s, ptt_e)

            new_model = model.replace(elements_old, elements_new)

            sce_name = '_automate_task_{}'.format(task)

            new_model_path = model_path.split('.')[0] + sce_name + '.bpmn'
            new_model_path = new_model_path.replace('inputs','inputs/automate_task/models')
            with open(new_model_path, 'w+') as new_file:
                new_file.write(new_model)
                
            csv_output_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/automate_task/output_{}.csv'.format(sce_name)
            u.execute_simulator_simple(bimp_path, new_model_path, csv_output_path)
            output_message = u.return_message_stats(csv_output_path, '{}'.format(' '.join(sce_name.split('_'))))

            csv_org_path = 'C:/CursosMaestria/Tesis/What-If-Chatbot/outputs/automate_task/output_baseline.csv'
            u.execute_simulator_simple(bimp_path, model_path, csv_org_path)
            org_message = u.return_message_stats(csv_org_path, 'Base')

            dispatcher.utter_message(text=org_message)
            dispatcher.utter_message(text=output_message)
        
        return []