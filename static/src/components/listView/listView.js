/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class LibraryListView extends Component {
    static template = "library.LibraryListView";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        const context = this.props.action.context || {};
        this.resModel = context.active_model || this.props.action.params?.model || "library.books";
        this.title = this.props.action.name || "Library Records";

        this.state = useState({
            records: [],
            formData: {},
            fields: [],
            relatedData: {},
        });

        onWillStart(async () => {
            await this.initComponent();
        });
    }

    async initComponent() {
        if (this.resModel === "library.books") {
            this.state.fields = [
                { name: "title", label: "Title", type: "char", required: true },
                { name: "isbn", label: "ISBN", type: "char", required: true },
                { name: "author_id", label: "Author", type: "many2one", relation: "library.author" },
                { name: "publisher_id", label: "Publisher", type: "many2one", relation: "library.publisher" },
                { name: "category_id", label: "Category", type: "many2one", relation: "library.book.category" },
                { name: "pages", label: "Pages", type: "integer", default: 100 },
                { name: "price", label: "Price", type: "float", default: 0 },
                { name: "copies", label: "Copies", type: "integer", default: 1 },
                { name: "available", label: "Available", type: "boolean", readonly: true },
            ];
        } else if (this.resModel === "library.author") {
            this.state.fields = [
                { name: "name", label: "Name", type: "char", required: true },
                { name: "date_of_birth", label: "Birthday", type: "date" },
                { name: "book_count", label: "Books Authored", type: "integer", readonly: true },
            ];
        } else if (this.resModel === "library.publisher") {
            this.state.fields = [
                { name: "name", label: "Publisher Name", type: "char", required: true },
            ];
        } else if (this.resModel === "library.member") {
            this.state.fields = [
                { name: "partner_id", label: "Partner", type: "many2one", relation: "res.partner", required: true },
                { name: "card_number", label: "Card #", type: "char", readonly: true },
                { name: "membership_type", label: "Type", type: "selection", selection: [['student', 'Student'], ['teacher', 'Teacher'], ['public', 'Public'], ['staff', 'Staff']] },
                { name: "state", label: "Status", type: "selection", selection: [['active', 'Active'], ['expired', 'Expired'], ['suspended', 'Suspended'], ['cancelled', 'Cancelled']] },
                { name: "membership_date", label: "Join Date", type: "date" },
                { name: "membership_expiry_date", label: "Expiry Date", type: "date" },
            ];
        } else if (this.resModel === "library.book.reservation") {
            this.state.fields = [
                { name: "name", label: "Ref", type: "char", readonly: true },
                { name: "member_id", label: "Member", type: "many2one", relation: "library.member", required: true },
                { name: "book_id", label: "Book", type: "many2one", relation: "library.books", required: true },
                { name: "reservation_date", label: "Date", type: "date" },
                { name: "expiry_date", label: "Expiry", type: "date", required: true },
                { name: "state", label: "Status", type: "selection", selection: [['pending', 'Pending'], ['confirmed', 'Confirmed'], ['cancelled', 'Cancelled'], ['expired', 'Expired'], ['fulfilled', 'Fulfilled']] },
            ];
        } else if (this.resModel === "borrowing.records") {
            this.state.fields = [
                { name: "name", label: "Rec #", type: "char", readonly: true },
                { name: "member_id", label: "Member", type: "many2one", relation: "library.member", required: true },
                { name: "date_borrowed", label: "Date Borrowed", type: "date" },
                { name: "date_expected_return", label: "Expected Return", type: "date", required: true },
                { name: "state", label: "Status", type: "selection", selection: [['draft', 'Draft'], ['borrowed', 'Borrowed'], ['fully_returned', 'Returned'], ['partially_returned', 'Partially Returned']] },
                { name: "total_fine", label: "Fine", type: "float", readonly: true },
            ];
        }

        this.resetForm();

        await this.loadRelatedData();

        await this.loadRecords();
    }

    resetForm() {
        const formData = {};
        this.state.fields.forEach(f => {
            if (!f.readonly) {
                formData[f.name] = f.default !== undefined ? f.default : (f.type === "many2one" ? false : "");
            }
            if (f.type === "many2one" && !this.state.relatedData[f.name]) {
                this.state.relatedData[f.name] = [];
            }
        });
        this.state.formData = formData;
    }

    async loadRecords() {
        try {
            const fieldNames = this.state.fields.map(f => f.name);
            this.state.records = await this.orm.searchRead(
                this.resModel,
                [],
                fieldNames,
                { order: "id desc" }
            );
        } catch (error) {
            this.notification.add(`Error loading ${this.resModel}: ` + error.message, { type: "danger" });
        }
    }

    async loadRelatedData() {
        try {
            for (const field of this.state.fields) {
                if (field.type === "many2one") {
                    this.state.relatedData[field.name] = await this.orm.searchRead(field.relation, [], ["display_name"]);
                }
            }
        } catch (error) {
            this.notification.add("Error loading selection data: " + error.message, { type: "danger" });
        }
    }

    async createRecord() {
        const missing = this.state.fields.filter(f => f.required && !this.state.formData[f.name]);
        if (missing.length > 0) {
            this.notification.add(`${missing.map(f => f.label).join(", ")} are required!`, { type: "warning" });
            return;
        }

        try {
            const vals = {};
            this.state.fields.forEach(f => {
                if (!f.readonly) {
                    let val = this.state.formData[f.name];
                    if (f.type === "many2one" || f.type === "integer") val = parseInt(val) || false;
                    if (f.type === "float") val = parseFloat(val) || 0;
                    vals[f.name] = val;
                }
            });

            await this.orm.create(this.resModel, [vals]);
            this.notification.add("Record created successfully!", { type: "success" });
            this.resetForm();
            await this.loadRecords();
        } catch (error) {
            this.notification.add("Error creating record: " + error.message, { type: "danger" });
        }
    }

    async deleteRecord(recordId) {
        if (!confirm("Are you sure you want to delete this record?")) {
            return;
        }

        try {
            await this.orm.unlink(this.resModel, [recordId]);
            this.notification.add("Record deleted successfully!", { type: "success" });
            await this.loadRecords();
        } catch (error) {
            this.notification.add("Error deleting record: " + error.message, { type: "danger" });
        }
    }

    updateFormField(field, value) {
        this.state.formData[field] = value;
    }

    getDisplayValue(record, field) {
        const val = record[field.name];
        if (field.type === "many2one") {
            if (Array.isArray(val)) return val[1];
            if (typeof val === "object" && val !== null) return val.display_name || val.name || JSON.stringify(val);
            return val || "-";
        }
        if (field.type === "selection") {
            const item = field.selection.find(s => s[0] === val);
            return item ? item[1] : val;
        }
        if (val === true) return "Yes";
        if (val === false) return "No";
        if (val === undefined || val === null) return "-";
        return val;
    }
}

registry.category("actions").add("library.generic_list_view", LibraryListView);
registry.category("actions").add("library.action_books_list_view", LibraryListView);