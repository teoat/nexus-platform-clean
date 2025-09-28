#!/usr/bin/env python3
"""
NEXUS Platform - Transaction Service
Business logic for transaction management
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from schemas.transaction import (TransactionBulkCreate, TransactionBulkUpdate,
                                 TransactionCreate, TransactionFilter,
                                 TransactionStats, TransactionSummary,
                                 TransactionType, TransactionUpdate)
from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Account, Category, Transaction

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

logger = logging.getLogger(__name__)


class TransactionService:
    """Service class for transaction operations"""

    def get_transactions(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[TransactionFilter] = None,
    ) -> List[Transaction]:
        """Get transactions with filtering and pagination"""
        try:
            query = db.query(Transaction).filter(Transaction.user_id == user_id)

            if filters:
                if filters.account_id:
                    query = query.filter(Transaction.account_id == filters.account_id)
                if filters.transaction_type:
                    query = query.filter(
                        Transaction.transaction_type == filters.transaction_type
                    )
                if filters.category:
                    query = query.filter(Transaction.category == filters.category)
                if filters.start_date:
                    query = query.filter(Transaction.date >= filters.start_date)
                if filters.end_date:
                    query = query.filter(Transaction.date <= filters.end_date)
                if filters.min_amount:
                    query = query.filter(Transaction.amount >= filters.min_amount)
                if filters.max_amount:
                    query = query.filter(Transaction.amount <= filters.max_amount)
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.filter(
                        or_(
                            Transaction.description.ilike(search_term),
                            Transaction.notes.ilike(search_term),
                        )
                    )

            return (
                query.order_by(desc(Transaction.date)).offset(skip).limit(limit).all()
            )
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise

    def get_transaction_by_id(
        self, db: Session, transaction_id: int, user_id: int
    ) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            return (
                db.query(Transaction)
                .filter(
                    and_(
                        Transaction.id == transaction_id, Transaction.user_id == user_id
                    )
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting transaction {transaction_id}: {e}")
            raise

    def create_transaction(
        self, db: Session, transaction_data: TransactionCreate, user_id: int
    ) -> Transaction:
        """Create a new transaction"""
        try:
            # Verify account belongs to user
            account = self.get_account_by_id(db, transaction_data.account_id, user_id)
            if not account:
                raise ValueError("Account not found or does not belong to user")

            # Create transaction
            transaction = Transaction(
                account_id=transaction_data.account_id,
                user_id=user_id,
                description=transaction_data.description,
                amount=transaction_data.amount,
                transaction_type=transaction_data.transaction_type,
                category=transaction_data.category,
                subcategory=transaction_data.subcategory,
                reference_number=transaction_data.reference_number,
                notes=transaction_data.notes,
                date=transaction_data.date,
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            # Update account balance
            self._update_account_balance(
                db,
                transaction_data.account_id,
                transaction_data.amount,
                transaction_data.transaction_type,
            )

            return transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise

    def update_transaction(
        self,
        db: Session,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int,
    ) -> Transaction:
        """Update transaction"""
        try:
            transaction = self.get_transaction_by_id(db, transaction_id, user_id)
            if not transaction:
                raise ValueError("Transaction not found")

            # Store old values for balance adjustment
            old_amount = transaction.amount
            old_type = transaction.transaction_type
            old_account_id = transaction.account_id

            # Update fields
            update_data = transaction_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(transaction, field, value)

            # Revert old balance change
            self._update_account_balance(db, old_account_id, -old_amount, old_type)

            # Apply new balance change
            new_amount = transaction.amount
            new_type = transaction.transaction_type
            new_account_id = transaction.account_id

            # If account changed, update both accounts
            if old_account_id != new_account_id:
                self._update_account_balance(db, new_account_id, new_amount, new_type)
            else:
                self._update_account_balance(db, new_account_id, new_amount, new_type)

            db.commit()
            db.refresh(transaction)

            return transaction
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating transaction {transaction_id}: {e}")
            raise

    def delete_transaction(
        self, db: Session, transaction_id: int, user_id: int
    ) -> bool:
        """Delete transaction"""
        try:
            transaction = self.get_transaction_by_id(db, transaction_id, user_id)
            if not transaction:
                raise ValueError("Transaction not found")

            # Revert balance change
            self._update_account_balance(
                db,
                transaction.account_id,
                -transaction.amount,
                transaction.transaction_type,
            )

            db.delete(transaction)
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting transaction {transaction_id}: {e}")
            raise

    def create_bulk_transactions(
        self, db: Session, transactions_data: List[TransactionCreate], user_id: int
    ) -> List[Transaction]:
        """Create multiple transactions"""
        try:
            transactions = []
            for transaction_data in transactions_data:
                # Verify account belongs to user
                account = self.get_account_by_id(
                    db, transaction_data.account_id, user_id
                )
                if not account:
                    raise ValueError(
                        f"Account {transaction_data.account_id} not found or does not belong to user"
                    )

                transaction = Transaction(
                    account_id=transaction_data.account_id,
                    user_id=user_id,
                    description=transaction_data.description,
                    amount=transaction_data.amount,
                    transaction_type=transaction_data.transaction_type,
                    category=transaction_data.category,
                    subcategory=transaction_data.subcategory,
                    reference_number=transaction_data.reference_number,
                    notes=transaction_data.notes,
                    date=transaction_data.date,
                )
                transactions.append(transaction)
                db.add(transaction)

            db.commit()

            # Update account balances
            for transaction in transactions:
                db.refresh(transaction)
                self._update_account_balance(
                    db,
                    transaction.account_id,
                    transaction.amount,
                    transaction.transaction_type,
                )

            return transactions
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating bulk transactions: {e}")
            raise

    def update_bulk_transactions(
        self,
        db: Session,
        transaction_ids: List[int],
        updates: TransactionUpdate,
        user_id: int,
    ) -> List[Transaction]:
        """Update multiple transactions"""
        try:
            transactions = []
            for transaction_id in transaction_ids:
                transaction = self.get_transaction_by_id(db, transaction_id, user_id)
                if not transaction:
                    continue

                # Store old values for balance adjustment
                old_amount = transaction.amount
                old_type = transaction.transaction_type
                old_account_id = transaction.account_id

                # Update fields
                update_data = updates.dict(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(transaction, field, value)

                # Revert old balance change
                self._update_account_balance(db, old_account_id, -old_amount, old_type)

                # Apply new balance change
                new_amount = transaction.amount
                new_type = transaction.transaction_type
                new_account_id = transaction.account_id

                # If account changed, update both accounts
                if old_account_id != new_account_id:
                    self._update_account_balance(
                        db, new_account_id, new_amount, new_type
                    )
                else:
                    self._update_account_balance(
                        db, new_account_id, new_amount, new_type
                    )

                transactions.append(transaction)

            db.commit()
            for transaction in transactions:
                db.refresh(transaction)

            return transactions
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating bulk transactions: {e}")
            raise

    def delete_bulk_transactions(
        self, db: Session, transaction_ids: List[int], user_id: int
    ) -> int:
        """Delete multiple transactions"""
        try:
            deleted_count = 0
            for transaction_id in transaction_ids:
                transaction = self.get_transaction_by_id(db, transaction_id, user_id)
                if not transaction:
                    continue

                # Revert balance change
                self._update_account_balance(
                    db,
                    transaction.account_id,
                    -transaction.amount,
                    transaction.transaction_type,
                )

                db.delete(transaction)
                deleted_count += 1

            db.commit()
            return deleted_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting bulk transactions: {e}")
            raise

    def get_transaction_stats(
        self,
        db: Session,
        user_id: int,
        account_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> TransactionStats:
        """Get transaction statistics"""
        try:
            query = db.query(Transaction).filter(Transaction.user_id == user_id)

            if account_id:
                query = query.filter(Transaction.account_id == account_id)

            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                query = query.filter(Transaction.date >= start_dt)

            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query = query.filter(Transaction.date <= end_dt)

            # Get current month stats
            now = datetime.utcnow()
            current_month_start = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            last_month_end = current_month_start - timedelta(seconds=1)

            # Total stats
            total_transactions = query.count()
            total_income = query.filter(
                Transaction.transaction_type == TransactionType.INCOME
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")
            total_expenses = query.filter(
                Transaction.transaction_type == TransactionType.EXPENSE
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")
            average_transaction = query.with_entities(
                func.avg(Transaction.amount)
            ).scalar() or Decimal("0")

            # Largest transactions
            largest_income = (
                query.filter(Transaction.transaction_type == TransactionType.INCOME)
                .with_entities(func.max(Transaction.amount))
                .scalar()
            )
            largest_expense = (
                query.filter(Transaction.transaction_type == TransactionType.EXPENSE)
                .with_entities(func.max(Transaction.amount))
                .scalar()
            )

            # Most used category
            most_used_category = (
                query.filter(Transaction.category.isnot(None))
                .with_entities(Transaction.category, func.count(Transaction.id))
                .group_by(Transaction.category)
                .order_by(desc(func.count(Transaction.id)))
                .first()
            )

            # Month over month stats
            current_month_txns = query.filter(
                Transaction.date >= current_month_start
            ).count()
            last_month_txns = query.filter(
                and_(
                    Transaction.date >= last_month_start,
                    Transaction.date <= last_month_end,
                )
            ).count()

            month_over_month_change = None
            if last_month_txns > 0:
                month_over_month_change = (
                    (current_month_txns - last_month_txns) / last_month_txns
                ) * 100

            return TransactionStats(
                total_transactions=total_transactions,
                total_income=total_income,
                total_expenses=total_expenses,
                average_transaction=average_transaction,
                largest_income=largest_income,
                largest_expense=largest_expense,
                most_used_category=most_used_category[0]
                if most_used_category
                else None,
                transactions_this_month=current_month_txns,
                transactions_last_month=last_month_txns,
                month_over_month_change=month_over_month_change,
            )
        except Exception as e:
            logger.error(f"Error getting transaction stats: {e}")
            raise

    def get_transaction_summary(
        self,
        db: Session,
        user_id: int,
        start_date: str,
        end_date: str,
        account_id: Optional[int] = None,
    ) -> TransactionSummary:
        """Get transaction summary for a period"""
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            query = db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_dt,
                    Transaction.date <= end_dt,
                )
            )

            if account_id:
                query = query.filter(Transaction.account_id == account_id)

            total_income = query.filter(
                Transaction.transaction_type == TransactionType.INCOME
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")
            total_expenses = query.filter(
                Transaction.transaction_type == TransactionType.EXPENSE
            ).with_entities(func.sum(Transaction.amount)).scalar() or Decimal("0")
            transaction_count = query.count()

            return TransactionSummary(
                total_income=total_income,
                total_expenses=total_expenses,
                net_amount=total_income - total_expenses,
                transaction_count=transaction_count,
                period_start=start_dt,
                period_end=end_dt,
            )
        except Exception as e:
            logger.error(f"Error getting transaction summary: {e}")
            raise

    def get_account_by_id(
        self, db: Session, account_id: int, user_id: int
    ) -> Optional[Account]:
        """Get account by ID and verify ownership"""
        try:
            return (
                db.query(Account)
                .filter(and_(Account.id == account_id, Account.user_id == user_id))
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting account {account_id}: {e}")
            raise

    def _update_account_balance(
        self,
        db: Session,
        account_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
    ):
        """Update account balance based on transaction"""
        try:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return

            # Determine if this increases or decreases the balance
            if transaction_type in [TransactionType.INCOME, TransactionType.ADJUSTMENT]:
                account.balance += amount
            elif transaction_type in [
                TransactionType.EXPENSE,
                TransactionType.TRANSFER,
            ]:
                account.balance -= amount

            db.commit()
        except Exception as e:
            logger.error(f"Error updating account balance: {e}")
            raise


# Create service instance
transaction_service = TransactionService()
