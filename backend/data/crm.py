class CRM:
    def __init__(self, company_id):
        """
        Initialize the CRM object with the company ID.

        Args:
        company_id (int): The ID of the company using the CRM.
        """
        self.company_id = company_id

    def complete_sync(self):
        """
        Generalized method for completing a sync.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")

    def get_access_token(self):
        """
        Generalized method for retrieving access token.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")

    def get_customers(self):
        """
        Generalized method to get customers.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")

    def get_invoices(self):
        """
        Generalized method to get invoices.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")

    def get_locations(self):
        """
        Generalized method to get locations.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")

    def get_equipment(self):
        """
        Generalized method to get equipment.
        This should be overridden by specific CRM implementations.

        Raises:
        NotImplementedError: If the method is not overridden in the subclass.
        """
        raise NotImplementedError(
            "This method should be overridden by a specific CRM class.")
