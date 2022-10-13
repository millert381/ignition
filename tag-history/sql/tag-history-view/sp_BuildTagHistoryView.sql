/****** Object:  StoredProcedure [dbo].[sp_BuildTagHistoryView]    Script Date: 9/28/2022 1:57:36 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Todd Miller, ECS Solutions
-- Create date: 9/6/2021
-- Description:	Dynamically update view to combine all 
--				Ignition Tag History partition tables
-- =============================================
ALTER PROCEDURE [dbo].[sp_BuildTagHistoryView]
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

	-- *** NOTE: The view (dbo.vwData) must already be created ***

    -- Dynamically update view
	DECLARE @sql nvarchar(max)
	SELECT @sql = SUBSTRING( 
	( 
		SELECT ' UNION SELECT * FROM ' + PNAME AS 'data()'
		FROM sqlth_partitions  p
		ORDER BY p.start_time
		FOR XML PATH('') 
	), 2 , 9999)

	SELECT @sql = rTRIM(@sql)
	SELECT @sql = SUBSTRING(@sql, 7, LEN(@sql))

	DECLARE @modifier varchar(20) = 'CREATE'
	IF EXISTS(select * FROM sys.views where name = 'vwData')
		SET @modifier = 'ALTER'

	SELECT @sql = @modifier + ' VIEW dbo.vwData ' + '
	AS 
	' + @sql + ';'

	--SELECT @sql
	exec sp_executesql @sql

END

