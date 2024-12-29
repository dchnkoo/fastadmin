# FastAdmin

**FastAdmin** is a framework for quickly creating administrative panels for FastAPI applications. It leverages SQLAlchemy for database management, Pydantic for data validation, and FastUI for generating React components. The framework automatically generates administrative interfaces based on SQLAlchemy tables, enabling easy integration with FastAPI applications.

## Key Features

- **Automatic Admin Panel Generation**: Automatically generates admin panels based on your database schema using SQLAlchemy and Pydantic models.
- **Integration with FastUI**: Creates React components from Pydantic models for the admin interface.
- **Easy Extensibility**: Provides a simple mechanism to add new features and components to the admin panel.
- **Pre-built Router for Admin Interface**: Automatically generated routes for FastAPI that provide a full-fledged admin interface for managing the database.
- **Support for Complex Pages via Jinja**: Allows using Jinja for more complex or customized pages in the admin panel.
- **Flexible Customization**: The `Page` class automatically tracks and updates the latest object for pages in the admin interface when inherited, enabling easy customization.

## How It Works

1. **SQLAlchemy Tables**: Define your database models using **FastAdminBase** and **FastColumn** or **fastadmin_mapped_column**.
2. **Conversion to Pydantic Models**: The framework automatically generates Pydantic models for each table, enabling data validation.
3. **FastUI Integration**: SQLAlchemy tables and Pydantic models are converted into React components using FastUI, allowing you to create an admin interface without manually writing React code.
4. **Pre-configured FastAPI Routers**: Pre-configured routes for the admin panel allow you to quickly deploy the interface in your application.
5. **Extensibility with `Page` Class**: Easily configure and extend the admin interface by using classes that automatically update their methods when inherited.