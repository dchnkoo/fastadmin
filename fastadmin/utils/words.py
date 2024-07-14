class AdminWords:
    def __init__(
        self,
        add: str = "Add",
        logout: str = "Logout",
        logout_question: str = "Are you sure do you want to logout?",
        cancel: str = "Cancel",
        additional_information: str = "Additional Information",
        delete: str = "Delete",
        confirm_operation: str = "Confirm operation",
        operation_delete_question: str = "Are you sure you wanna delete item with {field} - {value} from {table}?",
        back: str = "Back",
        edit: str = "Edit",
        form_page_heading: str = "Add to %s",
        edit_page_heading: str = "Edit %s",
        search: str = "Search",
        filter_text: str = "Filters",
        download_txt: str = "Download %s",
        download_title_modal: str = "Choose limit data for download",
    ) -> None:
        self.add = add
        self.logout = logout
        self.logout_question = logout_question
        self.cancel = cancel
        self.additional_information = additional_information
        self.delete = delete
        self.confirm_operation = confirm_operation
        self.operation_delete_question = operation_delete_question
        self.back = back
        self.edit = edit
        self.form_page_heading = form_page_heading
        self.edit_page_heading = edit_page_heading
        self.search = search
        self.filter_text = filter_text
        self.download_txt = download_txt
        self.download_title_modal = download_title_modal
