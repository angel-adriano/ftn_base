/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useGenerateRemittanceButton } from "./generate_remittance_hook";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";

// Scope the behavior to the remittance kanban only by providing a custom controller
class RemittanceKanbanController extends KanbanController {
    setup() {
        super.setup();
        useGenerateRemittanceButton();
    }
}

// Register a view variant bound to the js_class used in the XML
registry.category("views").add("account_remittance_kanban", {
    ...kanbanView,
    Controller: RemittanceKanbanController,
    buttonTemplate: "AccountRemittanceKanbanView.buttons",
});
