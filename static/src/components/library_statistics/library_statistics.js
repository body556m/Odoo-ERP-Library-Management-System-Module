/** @odoo-module **/

console.log("LibraryStatistics module loaded");

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LibraryStatistics extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");

        this.state = useState({
            booksCount: 0,
            lastUpdated: "Never",
        });

        this.intervalId = setInterval(() => {
            console.log("Working in Library...");
        }, 1000);

        onWillStart(async () => {
            this.state.booksCount = await this.rpc("/web/dataset/call_kw/library.books/search_count", {
                model: 'library.books',
                method: 'search_count',
                args: [[]],
                kwargs: {}
            });
            const now = new Date();
            this.state.lastUpdated = now.toLocaleString();
        });

        onWillUnmount(() => {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                console.log("Timer cleared - leaving Library screen");
            }
        });
    }

    async incrementBooks() {
        await this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'library.books',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current',
        });
    }
}

LibraryStatistics.template = "library.LibraryStatistics";

registry.category("actions").add("library.library_statistics", LibraryStatistics);
