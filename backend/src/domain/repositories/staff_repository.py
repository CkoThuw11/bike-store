from abc import ABC, abstractmethod
from src.domain.entities.staff import Staff
from typing import Optional, List


class IStaffRepository(ABC):
    """Abstract interface for Staff repository.
    
    This interface defines the contract for staff data access operations.
    Implementations must be provided in the Infrastructure layer.
    """
    @abstractmethod
    async def create(self, staff: Staff) -> Staff:
        """
        Adds a new staff member to the repository.
        
        Args:
            staff (Staff): The staff member to add.
        
        Returns:
            Staff: The added staff member.
        """
        pass

    @abstractmethod
    async def get_staff_by_id(self, staff_id: int) -> Optional[Staff]:
        """
        Retrieves a staff member by their ID.
        
        Args:
            staff_id (int): The ID of the staff member to retrieve.
        
        Returns:
            Staff: The retrieved staff member.
        """
        pass

    @abstractmethod
    async def get_staff_by_email(self, email: str) -> Optional[Staff]:
        """
        Retrieves a staff member by their email.
        
        Args:
            email (str): The email of the staff member to retrieve.
        
        Returns:
            Staff: The retrieved staff member.
        """
        pass

    @abstractmethod 
    async def get_staff_by_last_name(self, last_name: str) -> Optional[Staff]:
        """
        Retrieves a staff member by their last name.
        
        Args:
            last_name (str): The last name of the staff member to retrieve.
        
        Returns:
            Staff: The retrieved staff member.
        """
        pass

    @abstractmethod
    async def search_by_last_name(self, last_name: str) -> List[Staff]:
        """
        Retrieves staff members whose last name contains the given search term.

        Args:
            last_name (str): The search term to match against staff last names.

        Returns:
            List[Staff]: Staff members whose last name contains the search term.
        """
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Staff]:
        """
        Retrieves all staff members from the repository.
        
        Args:
            skip (int): The number of staff members to skip.
            limit (int): The maximum number of staff members to retrieve.
        
        Returns:
            list[Staff]: A list of all staff members.
        """
        pass

    @abstractmethod
    async def update(self, staff: Staff) -> Staff:
        """
        Updates an existing staff member in the repository.
        
        Args:
            staff (Staff): The staff member to update.
        
        Returns:
            Staff: The updated staff member.
        """
        pass

    @abstractmethod
    async def delete(self, staff_id: int) -> bool:
        """
        Deletes a staff member from the repository.
        
        Args:
            staff_id (int): The ID of the staff member to delete.
        
        Returns:
            bool: True if the staff member was deleted successfully, False otherwise.
        """
        pass