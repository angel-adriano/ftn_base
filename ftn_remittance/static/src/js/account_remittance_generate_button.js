/** @odoo-module **/

import { registry } from "@web/core/registry";
import { onMounted } from "@odoo/owl";

// Register a hook that triggers when the Kanban view is mounted
registry.category("view_hooks").add("account_remittance.kanban_button", {
    mounted({ env }) {
        onMounted(() => {
            // Find the "Generate Remittance" button inside the Kanban
            const button = document.querySelector(".o_button_generate_remittance");
            if (button) {
                button.addEventListener("click", () => {
                    // Replace with the real external ID of your wizard action
                    env.services.action.doAction("ftn_remittance.action_remittance_generate_wizard");
                });
            }
        });
    },
});
