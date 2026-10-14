-- arete_group database: user access list (3 users) and PO register (40 PO lines, Apr-Sep 2026).
-- Amounts are in INR without GST. All data is fictional (assignment data pack).
--
-- Tables are only created when they don't exist yet, so running this again never overwrites data.
--
--   sqlcmd -S localhost -E -C -i data\sql\arete_group.sql

IF DB_ID('arete_group') IS NULL
    CREATE DATABASE arete_group;
GO

USE arete_group;
GO

IF OBJECT_ID('dbo.user_access') IS NULL
BEGIN
    CREATE TABLE dbo.user_access (
        user_id            varchar(10)   NOT NULL PRIMARY KEY,
        name               varchar(100)  NOT NULL,
        department         varchar(50)   NULL,
        companies_allowed  varchar(50)   NULL,   -- 'C01', 'C02, C03' or 'All'
        remarks            varchar(255)  NULL
    );

    INSERT INTO dbo.user_access (user_id, name, department, companies_allowed, remarks) VALUES
    ('U01', 'Site user - Riverside', 'Projects', 'C01', NULL),
    ('U02', 'Pharma & retail user', 'Supply chain', 'C02, C03', 'shared service for both'),
    ('U03', 'Group finance user', 'Finance', 'All', 'group level access');
END
GO

IF OBJECT_ID('dbo.purchase_order_lines') IS NULL
BEGIN
    CREATE TABLE dbo.purchase_order_lines (
        id                 int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        company            varchar(10)    NOT NULL,
        purchase_order     varchar(30)    NOT NULL,
        po_date            date           NOT NULL,
        vendor_account     varchar(20)    NULL,
        vendor_name        nvarchar(150)  NULL,
        project_id         varchar(20)    NULL,
        project_name       nvarchar(100)  NULL,
        item_number        varchar(30)    NULL,
        item_description   nvarchar(150)  NULL,
        quantity           decimal(12,2)  NULL,
        unit               varchar(20)    NULL,
        unit_price         decimal(12,2)  NULL,
        line_amount_inr    decimal(14,2)  NULL,
        purchase_status    varchar(30)    NULL,   -- Open order, Received, Invoiced, Canceled
        buyer              varchar(50)    NULL,
        remarks            nvarchar(255)  NULL
    );

    SET IDENTITY_INSERT dbo.purchase_order_lines ON;

    INSERT INTO dbo.purchase_order_lines (id, company, purchase_order, po_date, vendor_account, vendor_name, project_id, project_name, item_number, item_description, quantity, unit, unit_price, line_amount_inr, purchase_status, buyer, remarks) VALUES
    (1, 'C02', 'GPL/PO/26-27/00120', '2026-04-01', 'V-00112', N'Shree Cement Traders', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'CEM-053', N'OPC Cement 53 grade', 103.00, 'Bag', 380.00, 39140.00, 'Invoiced', 'Anjali R', NULL),
    (2, 'C01', 'RIL/PO/26-27/00048', '2026-04-09', 'V-00203', N'Valsad Sand Suppliers', 'RIL-PRJ-0007', N'Riverside Towers', 'SND-RIV', N'River sand', 47.00, 'Brass', 4200.00, 197400.00, 'Invoiced', 'Kiran P', NULL),
    (3, 'C01', 'RIL/PO/26-27/00060', '2026-04-10', 'V-00145', N'GUJARAT STEEL ROLLING PVT. LTD.', NULL, NULL, 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 6.00, 'MT', 58000.00, 348000.00, 'Canceled', 'Mehul S', N'vendor could not supply'),
    (4, 'C01', 'RIL/PO/26-27/00054', '2026-04-12', 'V-00231', N'BuildPro Hardware', NULL, NULL, 'PLY-SHT18', N'Shuttering plywood 18 mm', 167.00, 'Sheet', 1350.00, 225450.00, 'Invoiced', 'Mehul S', NULL),
    (5, 'C01', 'RIL/PO/26-27/00045', '2026-04-21', 'V-00203', N'Valsad Sand Suppliers', 'RIL-PRJ-0007', N'Riverside Towers', 'SND-RIV', N'River sand', 54.00, 'Brass', 4200.00, 226800.00, 'Open order', 'Kiran P', N'rate revised after negotiation'),
    (6, 'C03', 'CRL/PO/26-27/00036', '2026-04-23', 'V-00427', N'CoolTech Refrigeration', 'CRL-PRJ-0002', N'Store Expansion Ph-2', 'EQP-CHL-2D', N'Display chiller 2 door', 4.00, 'Nos', 62000.00, 248000.00, 'Invoiced', 'Farhan K', NULL),
    (7, 'C02', 'GPL/PO/26-27/00147', '2026-05-06', 'V-00322', N'PackWell Industries', NULL, NULL, 'PM-ALU-BL', N'Alu blister foil', 115.00, 'Roll', 3100.00, 356500.00, 'Invoiced', 'Deepak M', N'partial qty recd'),
    (8, 'C03', 'CRL/PO/26-27/00034', '2026-05-17', 'V-00322', N'Packwell Industries', 'CRL-PRJ-0002', N'Store Expansion Ph-2', 'PM-CARRY-1K', N'Carry bags (pack of 1000)', 58.00, 'Pack', 1200.00, 69600.00, 'Open order', 'Farhan K', NULL),
    (9, 'C02', 'GPL/PO/26-27/00121', '2026-05-26', 'V-00322', N'PackWell Industries', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'PM-ALU-BL', N'Alu blister foil', 24.00, 'Roll', 3100.00, 74400.00, 'Invoiced', 'Anjali R', N'rate revised after negotiation'),
    (10, 'C01', 'RIL/PO/26-27/00066', '2026-05-27', 'V-00145', N'Gujarat Steel Rolling', 'RIL-PRJ-0011', N'Hilltop Bridge', 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 12.00, 'MT', 58000.00, 696000.00, 'Received', 'Kiran P', NULL),
    (11, 'C02', 'GPL/PO/26-27/00135', '2026-06-04', 'V-00112', N'Shree Cement Traders', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'CEM-053', N'OPC Cement 53 grade', 263.00, 'Bag', 380.00, 99940.00, 'Open order', 'Anjali R', N'partial qty recd'),
    (12, 'C03', 'CRL/PO/26-27/00031', '2026-06-08', 'V-00418', N'FreshMart Distributors', 'CRL-PRJ-0002', N'Store Expansion Ph-2', 'FMG-RICE25', N'Packaged rice 25 kg', 142.00, 'Bag', 1450.00, 205900.00, 'Open order', 'Farhan K', N'urgent - site work stopped'),
    (13, 'C02', 'GPL/PO/26-27/00118', '2026-06-11', 'V-00112', N'SHREE CEMENT TRADERS', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'CEM-053', N'OPC Cement 53 grade', 265.00, 'Bag', 380.00, 100700.00, 'Open order', 'Deepak M', NULL),
    (14, 'C02', 'GPL/PO/26-27/00124', '2026-06-14', 'V-00322', N'PackWell Industries', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'PM-ALU-BL', N'Alu blister foil', 90.00, 'Roll', 3100.00, 279000.00, 'Open order', 'Deepak M', NULL),
    (15, 'C03', 'CRL/PO/26-27/00051', '2026-06-26', 'V-00433', N'RackMaster Systems LLP', 'CRL-PRJ-0002', N'Store Expansion Ph-2', 'EQP-RACK-5', N'Storage rack 5 shelf', 27.00, 'Nos', 8900.00, 240300.00, 'Invoiced', 'Farhan K', N'pls expedite'),
    (16, 'C03', 'CRL/PO/26-27/00044', '2026-06-27', 'V-00433', N'Rackmaster Systems', NULL, NULL, 'EQP-RACK-5', N'Storage rack 5 shelf', 29.00, 'Nos', 8900.00, 258100.00, 'Invoiced', 'Farhan K', NULL),
    (17, 'C03', 'CRL/PO/26-27/00027', '2026-06-28', 'V-00433', N'RackMaster Systems LLP', NULL, NULL, 'EQP-RACK-5', N'Storage rack 5 shelf', 37.00, 'Nos', 8900.00, 329300.00, 'Received', 'Farhan K', N'pls expedite'),
    (18, 'C02', 'GPL/PO/26-27/00144', '2026-07-04', 'V-00322', N'Packwell Industries', NULL, NULL, 'PM-ALU-BL', N'Alu blister foil', 26.00, 'Roll', 3100.00, 80600.00, 'Invoiced', 'Deepak M', N'pls expedite'),
    (19, 'C03', 'CRL/PO/26-27/00039', '2026-07-09', 'V-00322', N'PackWell Industries', NULL, NULL, 'PM-CARRY-1K', N'Carry bags (pack of 1000)', 47.00, 'Pack', 1200.00, 56400.00, 'Open order', 'Farhan K', NULL),
    (20, 'C03', 'CRL/PO/26-27/00048', '2026-07-09', 'V-00322', N'Packwell Industries', NULL, NULL, 'PM-CARRY-1K', N'Carry bags (pack of 1000)', 29.00, 'Pack', 1200.00, 34800.00, 'Canceled', 'Farhan K', N'vendor could not supply'),
    (21, 'C01', 'RIL/PO/26-27/00044', '2026-07-12', 'V-00145', N'Gujarat Steel Rolling Pvt Ltd', 'RIL-PRJ-0007', N'Riverside Towers', 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 11.00, 'MT', 58000.00, 638000.00, 'Open order', 'Mehul S', N'partial qty recd'),
    (22, 'C03', 'CRL/PO/26-27/00025', '2026-07-17', 'V-00427', N'CoolTech Refrigeration', NULL, NULL, 'EQP-CHL-2D', N'Display chiller 2 door', 3.00, 'Nos', 62000.00, 186000.00, 'Invoiced', 'Farhan K', NULL),
    (23, 'C03', 'CRL/PO/26-27/00041', '2026-07-20', 'V-00427', N'CoolTech Refrigeration', NULL, NULL, 'EQP-CHL-2D', N'Display chiller 2 door', 1.00, 'Nos', 62000.00, 62000.00, 'Received', 'Farhan K', N'rate revised after negotiation'),
    (24, 'C02', 'GPL/PO/26-27/00128', '2026-07-26', 'V-00356', N'LabServe Instruments', NULL, NULL, 'LAB-HPLC-C18', N'HPLC column C18 250mm', 3.00, 'Nos', 48000.00, 144000.00, 'Canceled', 'Deepak M', N'cancelled as per PM'),
    (25, 'C01', 'RIL/PO/26-27/00059', '2026-08-01', 'V-00231', N'BuildPro Hardware', NULL, NULL, 'PLY-SHT18', N'Shuttering plywood 18 mm', 58.00, 'Sheet', 1350.00, 78300.00, 'Open order', 'Kiran P', NULL),
    (26, 'C01', 'RIL/PO/26-27/00041', '2026-08-02', 'V-00145', N'Gujarat Steel Rolling Pvt Ltd', 'RIL-PRJ-0007', N'Riverside Towers', 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 11.00, 'MT', 58000.00, 638000.00, 'Open order', 'Kiran P', N'pls expedite'),
    (27, 'C03', 'CRL/PO/26-27/00024', '2026-08-07', 'V-00427', N'CoolTech Refrigeration', NULL, NULL, 'EQP-CHL-2D', N'Display chiller 2 door', 4.00, 'Nos', 62000.00, 248000.00, 'Invoiced', 'Farhan K', N'rate as per agreement'),
    (28, 'C02', 'GPL/PO/26-27/00140', '2026-08-09', 'V-00112', N'Shree Cement Traders', NULL, NULL, 'CEM-053', N'OPC Cement 53 grade', 197.00, 'Bag', 380.00, 74860.00, 'Invoiced', 'Deepak M', NULL),
    (29, 'C02', 'GPL/PO/26-27/00132', '2026-08-10', 'V-00310', N'Apex Chemicals Pvt Ltd', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'RM-API-221', N'API intermediate GL-221', 358.00, 'Kg', 2400.00, 859200.00, 'Received', 'Anjali R', NULL),
    (30, 'C01', 'RIL/PO/26-27/00053', '2026-08-11', 'V-00231', N'BuildPro Hardware', 'RIL-PRJ-0007', N'Riverside Towers', 'PLY-SHT18', N'Shuttering plywood 18 mm', 144.00, 'Sheet', 1350.00, 194400.00, 'Invoiced', 'Kiran P', NULL),
    (31, 'C01', 'RIL/PO/26-27/00052', '2026-08-18', 'V-00145', N'Gujarat Steel Rolling', 'RIL-PRJ-0007', N'Riverside Towers', 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 8.00, 'MT', 58000.00, 464000.00, 'Open order', 'Mehul S', NULL),
    (32, 'C01', 'RIL/PO/26-27/00061', '2026-08-28', 'V-00203', N'Valsad Sand Suppliers', 'RIL-PRJ-0007', N'Riverside Towers', 'SND-RIV', N'River sand', 77.00, 'Brass', 4200.00, 323400.00, 'Open order', 'Mehul S', NULL),
    (33, 'C02', 'GPL/PO/26-27/00141', '2026-09-04', 'V-00356', N'LabServe Instruments', NULL, NULL, 'LAB-HPLC-C18', N'HPLC column C18 250mm', 2.00, 'Nos', 48000.00, 96000.00, 'Received', 'Anjali R', NULL),
    (34, 'C01', 'RIL/PO/26-27/00070', '2026-09-05', 'V-00203', N'Valsad Sand Suppliers', NULL, NULL, 'SND-RIV', N'River sand', 25.00, 'Brass', 4200.00, 105000.00, 'Invoiced', 'Mehul S', NULL),
    (35, 'C01', 'RIL/PO/26-27/00065', '2026-09-13', 'V-00112', N'Shree Cement Traders', 'RIL-PRJ-0011', N'Hilltop Bridge', 'CEM-053', N'OPC Cement 53 grade', 1404.00, 'Bag', 380.00, 533520.00, 'Received', 'Mehul S', N'rate revised after negotiation'),
    (36, 'C03', 'CRL/PO/26-27/00023', '2026-09-21', 'V-00427', N'CoolTech Refrigeration', 'CRL-PRJ-0002', N'Store Expansion Ph-2', 'EQP-CHL-2D', N'Display chiller 2 door', 1.00, 'Nos', 62000.00, 62000.00, 'Open order', 'Farhan K', NULL),
    (37, 'C01', 'RIL/PO/26-27/00055', '2026-09-23', 'V-00145', N'GUJARAT STEEL ROLLING PVT. LTD.', NULL, NULL, 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 13.00, 'MT', 58000.00, 754000.00, 'Received', 'Kiran P', N'pls expedite'),
    (38, 'C02', 'GPL/PO/26-27/00136', '2026-09-23', 'V-00310', N'Apex Chemicals', 'GPL-PRJ-0003', N'Plant 2 Upgrade', 'RM-API-221', N'API intermediate GL-221', 118.00, 'Kg', 2400.00, 283200.00, 'Invoiced', 'Anjali R', NULL),
    (39, 'C02', 'GPL/PO/26-27/00122', '2026-09-24', 'V-00112', N'Shree Cement Traders', NULL, NULL, 'CEM-053', N'OPC Cement 53 grade', 374.00, 'Bag', 380.00, 142120.00, 'Open order', 'Deepak M', N'rate as per agreement'),
    (40, 'C01', 'RIL/PO/26-27/00042', '2026-09-28', 'V-00145', N'Gujarat Steel Rolling Pvt Ltd', 'RIL-PRJ-0007', N'Riverside Towers', 'STL-TMT12', N'TMT Bar 12 mm Fe500D', 18.00, 'MT', 58000.00, 1044000.00, 'Open order', 'Mehul S', N'rate as per agreement');

    SET IDENTITY_INSERT dbo.purchase_order_lines OFF;
END
GO
