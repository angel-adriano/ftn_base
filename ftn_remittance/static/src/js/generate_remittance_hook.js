/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { useComponent } from "@odoo/owl";

export function useGenerateRemittanceButton() {
    const component = useComponent();
    const action = useService("action");

    // Define the handler directly during setup
    component.onClickGenerateRemittance = () => {
        action.doAction({
            name: "Generate remittance",
            type: "ir.actions.act_window",
            res_model: "account.remittance.generate.wizard",
            target: "new",
            views: [[false, "form"]],
        });
    };
}

