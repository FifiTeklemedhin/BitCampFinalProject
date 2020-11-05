-- Create a new table called 'ScrapedData' in schema 'ScrapedSchema'
-- Drop the table if it already exists
IF OBJECT_ID('dbo.ScrapedData', 'U') IS NOT NULL
DROP TABLE dbo.ScrapedData
GO
-- Create the table in the specified schema
CREATE TABLE dbo.ScrapedData
(
    TableNameId INT NOT NULL PRIMARY KEY, -- primary key column
    Column1 [NVARCHAR](50) NOT NULL,
    Column2 [NVARCHAR](50) NOT NULL
    -- specify more columns here
);
GO