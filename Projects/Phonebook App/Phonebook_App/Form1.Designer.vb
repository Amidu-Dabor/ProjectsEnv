<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim First_NameLabel As System.Windows.Forms.Label
        Dim Last_NameLabel As System.Windows.Forms.Label
        Dim Phone_NumberLabel As System.Windows.Forms.Label
        Dim Email_AddressLabel As System.Windows.Forms.Label
        Dim Home_AddressLabel As System.Windows.Forms.Label
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Form1))
        Dim Label1 As System.Windows.Forms.Label
        Dim Label2 As System.Windows.Forms.Label
        Me.PhonebookTableBindingNavigator = New System.Windows.Forms.BindingNavigator(Me.components)
        Me.BindingNavigatorAddNewItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorCountItem = New System.Windows.Forms.ToolStripLabel()
        Me.BindingNavigatorDeleteItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorMoveFirstItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorMovePreviousItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorSeparator = New System.Windows.Forms.ToolStripSeparator()
        Me.BindingNavigatorPositionItem = New System.Windows.Forms.ToolStripTextBox()
        Me.BindingNavigatorSeparator1 = New System.Windows.Forms.ToolStripSeparator()
        Me.BindingNavigatorMoveNextItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorMoveLastItem = New System.Windows.Forms.ToolStripButton()
        Me.BindingNavigatorSeparator2 = New System.Windows.Forms.ToolStripSeparator()
        Me.PhonebookTableBindingNavigatorSaveItem = New System.Windows.Forms.ToolStripButton()
        Me.First_NameTextBox = New System.Windows.Forms.TextBox()
        Me.Last_NameTextBox = New System.Windows.Forms.TextBox()
        Me.Phone_NumberTextBox = New System.Windows.Forms.TextBox()
        Me.Email_AddressTextBox = New System.Windows.Forms.TextBox()
        Me.Home_AddressTextBox = New System.Windows.Forms.TextBox()
        Me.Button1 = New System.Windows.Forms.Button()
        Me.Button2 = New System.Windows.Forms.Button()
        Me.Button3 = New System.Windows.Forms.Button()
        Me.Button4 = New System.Windows.Forms.Button()
        Me.Button5 = New System.Windows.Forms.Button()
        Me.Panel1 = New System.Windows.Forms.Panel()
        Me.Button6 = New System.Windows.Forms.Button()
        Me.DataGridView1 = New System.Windows.Forms.DataGridView()
        Me.FirstNameDataGridViewTextBoxColumn = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.LastNameDataGridViewTextBoxColumn = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.PhoneNumberDataGridViewTextBoxColumn = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.EmailAddressDataGridViewTextBoxColumn = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.HomeAddressDataGridViewTextBoxColumn = New System.Windows.Forms.DataGridViewTextBoxColumn()
        Me.PhonebookTableBindingSource1 = New System.Windows.Forms.BindingSource(Me.components)
        Me.PhonebookDataSet1 = New Phonebook_App.PhonebookDataSet1()
        Me.PhonebookTableBindingSource = New System.Windows.Forms.BindingSource(Me.components)
        Me.PhonebookTableTableAdapter = New Phonebook_App.PhonebookDataSet1TableAdapters.PhonebookTableTableAdapter()
        Me.TableAdapterManager = New Phonebook_App.PhonebookDataSet1TableAdapters.TableAdapterManager()
        Me.PhonebookDataSet1BindingSource = New System.Windows.Forms.BindingSource(Me.components)
        First_NameLabel = New System.Windows.Forms.Label()
        Last_NameLabel = New System.Windows.Forms.Label()
        Phone_NumberLabel = New System.Windows.Forms.Label()
        Email_AddressLabel = New System.Windows.Forms.Label()
        Home_AddressLabel = New System.Windows.Forms.Label()
        Label1 = New System.Windows.Forms.Label()
        Label2 = New System.Windows.Forms.Label()
        CType(Me.PhonebookTableBindingNavigator, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.PhonebookTableBindingNavigator.SuspendLayout()
        Me.Panel1.SuspendLayout()
        CType(Me.DataGridView1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.PhonebookTableBindingSource1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.PhonebookDataSet1, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.PhonebookTableBindingSource, System.ComponentModel.ISupportInitialize).BeginInit()
        CType(Me.PhonebookDataSet1BindingSource, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'First_NameLabel
        '
        First_NameLabel.AutoSize = True
        First_NameLabel.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        First_NameLabel.Location = New System.Drawing.Point(40, 56)
        First_NameLabel.Name = "First_NameLabel"
        First_NameLabel.Size = New System.Drawing.Size(94, 24)
        First_NameLabel.TabIndex = 1
        First_NameLabel.Text = "First Name:"
        '
        'Last_NameLabel
        '
        Last_NameLabel.AutoSize = True
        Last_NameLabel.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Last_NameLabel.Location = New System.Drawing.Point(42, 96)
        Last_NameLabel.Name = "Last_NameLabel"
        Last_NameLabel.Size = New System.Drawing.Size(92, 24)
        Last_NameLabel.TabIndex = 3
        Last_NameLabel.Text = "Last Name:"
        '
        'Phone_NumberLabel
        '
        Phone_NumberLabel.AutoSize = True
        Phone_NumberLabel.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Phone_NumberLabel.Location = New System.Drawing.Point(12, 136)
        Phone_NumberLabel.Name = "Phone_NumberLabel"
        Phone_NumberLabel.Size = New System.Drawing.Size(122, 24)
        Phone_NumberLabel.TabIndex = 5
        Phone_NumberLabel.Text = "Phone Number:"
        '
        'Email_AddressLabel
        '
        Email_AddressLabel.AutoSize = True
        Email_AddressLabel.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Email_AddressLabel.Location = New System.Drawing.Point(15, 176)
        Email_AddressLabel.Name = "Email_AddressLabel"
        Email_AddressLabel.Size = New System.Drawing.Size(119, 24)
        Email_AddressLabel.TabIndex = 7
        Email_AddressLabel.Text = "Email Address:"
        '
        'Home_AddressLabel
        '
        Home_AddressLabel.AutoSize = True
        Home_AddressLabel.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Home_AddressLabel.Location = New System.Drawing.Point(14, 216)
        Home_AddressLabel.Name = "Home_AddressLabel"
        Home_AddressLabel.Size = New System.Drawing.Size(120, 24)
        Home_AddressLabel.TabIndex = 9
        Home_AddressLabel.Text = "Home Address:"
        '
        'PhonebookTableBindingNavigator
        '
        Me.PhonebookTableBindingNavigator.AddNewItem = Me.BindingNavigatorAddNewItem
        Me.PhonebookTableBindingNavigator.BindingSource = Me.PhonebookTableBindingSource
        Me.PhonebookTableBindingNavigator.CountItem = Me.BindingNavigatorCountItem
        Me.PhonebookTableBindingNavigator.DeleteItem = Me.BindingNavigatorDeleteItem
        Me.PhonebookTableBindingNavigator.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.BindingNavigatorMoveFirstItem, Me.BindingNavigatorMovePreviousItem, Me.BindingNavigatorSeparator, Me.BindingNavigatorPositionItem, Me.BindingNavigatorCountItem, Me.BindingNavigatorSeparator1, Me.BindingNavigatorMoveNextItem, Me.BindingNavigatorMoveLastItem, Me.BindingNavigatorSeparator2, Me.BindingNavigatorAddNewItem, Me.BindingNavigatorDeleteItem, Me.PhonebookTableBindingNavigatorSaveItem})
        Me.PhonebookTableBindingNavigator.Location = New System.Drawing.Point(0, 0)
        Me.PhonebookTableBindingNavigator.MoveFirstItem = Me.BindingNavigatorMoveFirstItem
        Me.PhonebookTableBindingNavigator.MoveLastItem = Me.BindingNavigatorMoveLastItem
        Me.PhonebookTableBindingNavigator.MoveNextItem = Me.BindingNavigatorMoveNextItem
        Me.PhonebookTableBindingNavigator.MovePreviousItem = Me.BindingNavigatorMovePreviousItem
        Me.PhonebookTableBindingNavigator.Name = "PhonebookTableBindingNavigator"
        Me.PhonebookTableBindingNavigator.PositionItem = Me.BindingNavigatorPositionItem
        Me.PhonebookTableBindingNavigator.Size = New System.Drawing.Size(800, 25)
        Me.PhonebookTableBindingNavigator.TabIndex = 0
        Me.PhonebookTableBindingNavigator.Text = "BindingNavigator1"
        Me.PhonebookTableBindingNavigator.Visible = False
        '
        'BindingNavigatorAddNewItem
        '
        Me.BindingNavigatorAddNewItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorAddNewItem.Image = CType(resources.GetObject("BindingNavigatorAddNewItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorAddNewItem.Name = "BindingNavigatorAddNewItem"
        Me.BindingNavigatorAddNewItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorAddNewItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorAddNewItem.Text = "Add new"
        '
        'BindingNavigatorCountItem
        '
        Me.BindingNavigatorCountItem.Name = "BindingNavigatorCountItem"
        Me.BindingNavigatorCountItem.Size = New System.Drawing.Size(35, 22)
        Me.BindingNavigatorCountItem.Text = "of {0}"
        Me.BindingNavigatorCountItem.ToolTipText = "Total number of items"
        '
        'BindingNavigatorDeleteItem
        '
        Me.BindingNavigatorDeleteItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorDeleteItem.Image = CType(resources.GetObject("BindingNavigatorDeleteItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorDeleteItem.Name = "BindingNavigatorDeleteItem"
        Me.BindingNavigatorDeleteItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorDeleteItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorDeleteItem.Text = "Delete"
        '
        'BindingNavigatorMoveFirstItem
        '
        Me.BindingNavigatorMoveFirstItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorMoveFirstItem.Image = CType(resources.GetObject("BindingNavigatorMoveFirstItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorMoveFirstItem.Name = "BindingNavigatorMoveFirstItem"
        Me.BindingNavigatorMoveFirstItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorMoveFirstItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorMoveFirstItem.Text = "Move first"
        '
        'BindingNavigatorMovePreviousItem
        '
        Me.BindingNavigatorMovePreviousItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorMovePreviousItem.Image = CType(resources.GetObject("BindingNavigatorMovePreviousItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorMovePreviousItem.Name = "BindingNavigatorMovePreviousItem"
        Me.BindingNavigatorMovePreviousItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorMovePreviousItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorMovePreviousItem.Text = "Move previous"
        '
        'BindingNavigatorSeparator
        '
        Me.BindingNavigatorSeparator.Name = "BindingNavigatorSeparator"
        Me.BindingNavigatorSeparator.Size = New System.Drawing.Size(6, 25)
        '
        'BindingNavigatorPositionItem
        '
        Me.BindingNavigatorPositionItem.AccessibleName = "Position"
        Me.BindingNavigatorPositionItem.AutoSize = False
        Me.BindingNavigatorPositionItem.Font = New System.Drawing.Font("Segoe UI", 9.0!)
        Me.BindingNavigatorPositionItem.Name = "BindingNavigatorPositionItem"
        Me.BindingNavigatorPositionItem.Size = New System.Drawing.Size(50, 23)
        Me.BindingNavigatorPositionItem.Text = "0"
        Me.BindingNavigatorPositionItem.ToolTipText = "Current position"
        '
        'BindingNavigatorSeparator1
        '
        Me.BindingNavigatorSeparator1.Name = "BindingNavigatorSeparator1"
        Me.BindingNavigatorSeparator1.Size = New System.Drawing.Size(6, 25)
        '
        'BindingNavigatorMoveNextItem
        '
        Me.BindingNavigatorMoveNextItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorMoveNextItem.Image = CType(resources.GetObject("BindingNavigatorMoveNextItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorMoveNextItem.Name = "BindingNavigatorMoveNextItem"
        Me.BindingNavigatorMoveNextItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorMoveNextItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorMoveNextItem.Text = "Move next"
        '
        'BindingNavigatorMoveLastItem
        '
        Me.BindingNavigatorMoveLastItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.BindingNavigatorMoveLastItem.Image = CType(resources.GetObject("BindingNavigatorMoveLastItem.Image"), System.Drawing.Image)
        Me.BindingNavigatorMoveLastItem.Name = "BindingNavigatorMoveLastItem"
        Me.BindingNavigatorMoveLastItem.RightToLeftAutoMirrorImage = True
        Me.BindingNavigatorMoveLastItem.Size = New System.Drawing.Size(23, 22)
        Me.BindingNavigatorMoveLastItem.Text = "Move last"
        '
        'BindingNavigatorSeparator2
        '
        Me.BindingNavigatorSeparator2.Name = "BindingNavigatorSeparator2"
        Me.BindingNavigatorSeparator2.Size = New System.Drawing.Size(6, 25)
        '
        'PhonebookTableBindingNavigatorSaveItem
        '
        Me.PhonebookTableBindingNavigatorSaveItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.PhonebookTableBindingNavigatorSaveItem.Image = CType(resources.GetObject("PhonebookTableBindingNavigatorSaveItem.Image"), System.Drawing.Image)
        Me.PhonebookTableBindingNavigatorSaveItem.Name = "PhonebookTableBindingNavigatorSaveItem"
        Me.PhonebookTableBindingNavigatorSaveItem.Size = New System.Drawing.Size(23, 22)
        Me.PhonebookTableBindingNavigatorSaveItem.Text = "Save Data"
        '
        'First_NameTextBox
        '
        Me.First_NameTextBox.DataBindings.Add(New System.Windows.Forms.Binding("Text", Me.PhonebookTableBindingSource, "First_Name", True))
        Me.First_NameTextBox.Location = New System.Drawing.Point(140, 56)
        Me.First_NameTextBox.Multiline = True
        Me.First_NameTextBox.Name = "First_NameTextBox"
        Me.First_NameTextBox.Size = New System.Drawing.Size(293, 24)
        Me.First_NameTextBox.TabIndex = 2
        '
        'Last_NameTextBox
        '
        Me.Last_NameTextBox.DataBindings.Add(New System.Windows.Forms.Binding("Text", Me.PhonebookTableBindingSource, "Last_Name", True))
        Me.Last_NameTextBox.Location = New System.Drawing.Point(140, 96)
        Me.Last_NameTextBox.Multiline = True
        Me.Last_NameTextBox.Name = "Last_NameTextBox"
        Me.Last_NameTextBox.Size = New System.Drawing.Size(293, 24)
        Me.Last_NameTextBox.TabIndex = 4
        '
        'Phone_NumberTextBox
        '
        Me.Phone_NumberTextBox.DataBindings.Add(New System.Windows.Forms.Binding("Text", Me.PhonebookTableBindingSource, "Phone_Number", True))
        Me.Phone_NumberTextBox.Location = New System.Drawing.Point(140, 136)
        Me.Phone_NumberTextBox.Multiline = True
        Me.Phone_NumberTextBox.Name = "Phone_NumberTextBox"
        Me.Phone_NumberTextBox.Size = New System.Drawing.Size(293, 24)
        Me.Phone_NumberTextBox.TabIndex = 6
        '
        'Email_AddressTextBox
        '
        Me.Email_AddressTextBox.DataBindings.Add(New System.Windows.Forms.Binding("Text", Me.PhonebookTableBindingSource, "Email_Address", True))
        Me.Email_AddressTextBox.Location = New System.Drawing.Point(140, 176)
        Me.Email_AddressTextBox.Multiline = True
        Me.Email_AddressTextBox.Name = "Email_AddressTextBox"
        Me.Email_AddressTextBox.Size = New System.Drawing.Size(293, 24)
        Me.Email_AddressTextBox.TabIndex = 8
        '
        'Home_AddressTextBox
        '
        Me.Home_AddressTextBox.DataBindings.Add(New System.Windows.Forms.Binding("Text", Me.PhonebookTableBindingSource, "Home_Address", True))
        Me.Home_AddressTextBox.Location = New System.Drawing.Point(140, 216)
        Me.Home_AddressTextBox.Multiline = True
        Me.Home_AddressTextBox.Name = "Home_AddressTextBox"
        Me.Home_AddressTextBox.Size = New System.Drawing.Size(293, 24)
        Me.Home_AddressTextBox.TabIndex = 10
        '
        'Button1
        '
        Me.Button1.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button1.Location = New System.Drawing.Point(16, 294)
        Me.Button1.Name = "Button1"
        Me.Button1.Size = New System.Drawing.Size(119, 48)
        Me.Button1.TabIndex = 11
        Me.Button1.Text = "Save"
        Me.Button1.UseVisualStyleBackColor = True
        '
        'Button2
        '
        Me.Button2.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button2.Location = New System.Drawing.Point(138, 294)
        Me.Button2.Name = "Button2"
        Me.Button2.Size = New System.Drawing.Size(119, 48)
        Me.Button2.TabIndex = 12
        Me.Button2.Text = "Previous"
        Me.Button2.UseVisualStyleBackColor = True
        '
        'Button3
        '
        Me.Button3.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button3.Location = New System.Drawing.Point(263, 294)
        Me.Button3.Name = "Button3"
        Me.Button3.Size = New System.Drawing.Size(119, 48)
        Me.Button3.TabIndex = 13
        Me.Button3.Text = "Next"
        Me.Button3.UseVisualStyleBackColor = True
        '
        'Button4
        '
        Me.Button4.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button4.Location = New System.Drawing.Point(388, 294)
        Me.Button4.Name = "Button4"
        Me.Button4.Size = New System.Drawing.Size(119, 48)
        Me.Button4.TabIndex = 14
        Me.Button4.Text = "Delete"
        Me.Button4.UseVisualStyleBackColor = True
        '
        'Button5
        '
        Me.Button5.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button5.Location = New System.Drawing.Point(4, 336)
        Me.Button5.Name = "Button5"
        Me.Button5.Size = New System.Drawing.Size(366, 60)
        Me.Button5.TabIndex = 15
        Me.Button5.Text = "Add New Contact"
        Me.Button5.UseVisualStyleBackColor = True
        '
        'Panel1
        '
        Me.Panel1.BackColor = System.Drawing.SystemColors.GradientInactiveCaption
        Me.Panel1.Controls.Add(Label1)
        Me.Panel1.Controls.Add(Me.Button5)
        Me.Panel1.Controls.Add(Me.Button6)
        Me.Panel1.Controls.Add(Me.Home_AddressTextBox)
        Me.Panel1.Controls.Add(Me.First_NameTextBox)
        Me.Panel1.Controls.Add(Me.Last_NameTextBox)
        Me.Panel1.Controls.Add(Me.Phone_NumberTextBox)
        Me.Panel1.Controls.Add(Me.Email_AddressTextBox)
        Me.Panel1.Controls.Add(Home_AddressLabel)
        Me.Panel1.Controls.Add(Email_AddressLabel)
        Me.Panel1.Controls.Add(Phone_NumberLabel)
        Me.Panel1.Controls.Add(Last_NameLabel)
        Me.Panel1.Controls.Add(First_NameLabel)
        Me.Panel1.Location = New System.Drawing.Point(12, 12)
        Me.Panel1.Name = "Panel1"
        Me.Panel1.Size = New System.Drawing.Size(504, 426)
        Me.Panel1.TabIndex = 16
        '
        'Button6
        '
        Me.Button6.Font = New System.Drawing.Font("Franklin Gothic Demi", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Button6.Location = New System.Drawing.Point(376, 336)
        Me.Button6.Name = "Button6"
        Me.Button6.Size = New System.Drawing.Size(119, 60)
        Me.Button6.TabIndex = 17
        Me.Button6.Text = "Exit"
        Me.Button6.UseVisualStyleBackColor = True
        '
        'DataGridView1
        '
        Me.DataGridView1.AutoGenerateColumns = False
        Me.DataGridView1.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.DataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.DataGridView1.Columns.AddRange(New System.Windows.Forms.DataGridViewColumn() {Me.FirstNameDataGridViewTextBoxColumn, Me.LastNameDataGridViewTextBoxColumn, Me.PhoneNumberDataGridViewTextBoxColumn, Me.EmailAddressDataGridViewTextBoxColumn, Me.HomeAddressDataGridViewTextBoxColumn})
        Me.DataGridView1.DataSource = Me.PhonebookTableBindingSource1
        Me.DataGridView1.Location = New System.Drawing.Point(522, 53)
        Me.DataGridView1.Name = "DataGridView1"
        Me.DataGridView1.Size = New System.Drawing.Size(574, 355)
        Me.DataGridView1.TabIndex = 17
        '
        'Label1
        '
        Label1.AutoSize = True
        Label1.BackColor = System.Drawing.SystemColors.ButtonFace
        Label1.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 18.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Label1.Location = New System.Drawing.Point(192, 10)
        Label1.Name = "Label1"
        Label1.Size = New System.Drawing.Size(128, 30)
        Label1.TabIndex = 18
        Label1.Text = "PHONEBOOK"
        '
        'Label2
        '
        Label2.AutoSize = True
        Label2.BackColor = System.Drawing.SystemColors.ButtonFace
        Label2.Font = New System.Drawing.Font("Franklin Gothic Demi Cond", 18.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Label2.Location = New System.Drawing.Point(665, 9)
        Label2.Name = "Label2"
        Label2.Size = New System.Drawing.Size(296, 30)
        Label2.TabIndex = 19
        Label2.Text = "LIST OF PHONEBOOK CONTACTS"
        '
        'FirstNameDataGridViewTextBoxColumn
        '
        Me.FirstNameDataGridViewTextBoxColumn.DataPropertyName = "First_Name"
        Me.FirstNameDataGridViewTextBoxColumn.HeaderText = "First_Name"
        Me.FirstNameDataGridViewTextBoxColumn.Name = "FirstNameDataGridViewTextBoxColumn"
        '
        'LastNameDataGridViewTextBoxColumn
        '
        Me.LastNameDataGridViewTextBoxColumn.DataPropertyName = "Last_Name"
        Me.LastNameDataGridViewTextBoxColumn.HeaderText = "Last_Name"
        Me.LastNameDataGridViewTextBoxColumn.Name = "LastNameDataGridViewTextBoxColumn"
        '
        'PhoneNumberDataGridViewTextBoxColumn
        '
        Me.PhoneNumberDataGridViewTextBoxColumn.DataPropertyName = "Phone_Number"
        Me.PhoneNumberDataGridViewTextBoxColumn.HeaderText = "Phone_Number"
        Me.PhoneNumberDataGridViewTextBoxColumn.Name = "PhoneNumberDataGridViewTextBoxColumn"
        '
        'EmailAddressDataGridViewTextBoxColumn
        '
        Me.EmailAddressDataGridViewTextBoxColumn.DataPropertyName = "Email_Address"
        Me.EmailAddressDataGridViewTextBoxColumn.HeaderText = "Email_Address"
        Me.EmailAddressDataGridViewTextBoxColumn.Name = "EmailAddressDataGridViewTextBoxColumn"
        '
        'HomeAddressDataGridViewTextBoxColumn
        '
        Me.HomeAddressDataGridViewTextBoxColumn.DataPropertyName = "Home_Address"
        Me.HomeAddressDataGridViewTextBoxColumn.HeaderText = "Home_Address"
        Me.HomeAddressDataGridViewTextBoxColumn.Name = "HomeAddressDataGridViewTextBoxColumn"
        '
        'PhonebookTableBindingSource1
        '
        Me.PhonebookTableBindingSource1.DataMember = "PhonebookTable"
        Me.PhonebookTableBindingSource1.DataSource = Me.PhonebookDataSet1
        '
        'PhonebookDataSet1
        '
        Me.PhonebookDataSet1.DataSetName = "PhonebookDataSet1"
        Me.PhonebookDataSet1.SchemaSerializationMode = System.Data.SchemaSerializationMode.IncludeSchema
        '
        'PhonebookTableBindingSource
        '
        Me.PhonebookTableBindingSource.DataMember = "PhonebookTable"
        Me.PhonebookTableBindingSource.DataSource = Me.PhonebookDataSet1
        '
        'PhonebookTableTableAdapter
        '
        Me.PhonebookTableTableAdapter.ClearBeforeFill = True
        '
        'TableAdapterManager
        '
        Me.TableAdapterManager.BackupDataSetBeforeUpdate = False
        Me.TableAdapterManager.PhonebookTableTableAdapter = Me.PhonebookTableTableAdapter
        Me.TableAdapterManager.UpdateOrder = Phonebook_App.PhonebookDataSet1TableAdapters.TableAdapterManager.UpdateOrderOption.InsertUpdateDelete
        '
        'PhonebookDataSet1BindingSource
        '
        Me.PhonebookDataSet1BindingSource.DataSource = Me.PhonebookDataSet1
        Me.PhonebookDataSet1BindingSource.Position = 0
        '
        'Form1
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(1108, 450)
        Me.Controls.Add(Label2)
        Me.Controls.Add(Me.DataGridView1)
        Me.Controls.Add(Me.Button4)
        Me.Controls.Add(Me.Button3)
        Me.Controls.Add(Me.Button2)
        Me.Controls.Add(Me.Button1)
        Me.Controls.Add(Me.PhonebookTableBindingNavigator)
        Me.Controls.Add(Me.Panel1)
        Me.Name = "Form1"
        Me.Text = "Form1"
        CType(Me.PhonebookTableBindingNavigator, System.ComponentModel.ISupportInitialize).EndInit()
        Me.PhonebookTableBindingNavigator.ResumeLayout(False)
        Me.PhonebookTableBindingNavigator.PerformLayout()
        Me.Panel1.ResumeLayout(False)
        Me.Panel1.PerformLayout()
        CType(Me.DataGridView1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.PhonebookTableBindingSource1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.PhonebookDataSet1, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.PhonebookTableBindingSource, System.ComponentModel.ISupportInitialize).EndInit()
        CType(Me.PhonebookDataSet1BindingSource, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents PhonebookDataSet1 As PhonebookDataSet1
    Friend WithEvents PhonebookTableBindingSource As BindingSource
    Friend WithEvents PhonebookTableTableAdapter As PhonebookDataSet1TableAdapters.PhonebookTableTableAdapter
    Friend WithEvents TableAdapterManager As PhonebookDataSet1TableAdapters.TableAdapterManager
    Friend WithEvents PhonebookTableBindingNavigator As BindingNavigator
    Friend WithEvents BindingNavigatorAddNewItem As ToolStripButton
    Friend WithEvents BindingNavigatorCountItem As ToolStripLabel
    Friend WithEvents BindingNavigatorDeleteItem As ToolStripButton
    Friend WithEvents BindingNavigatorMoveFirstItem As ToolStripButton
    Friend WithEvents BindingNavigatorMovePreviousItem As ToolStripButton
    Friend WithEvents BindingNavigatorSeparator As ToolStripSeparator
    Friend WithEvents BindingNavigatorPositionItem As ToolStripTextBox
    Friend WithEvents BindingNavigatorSeparator1 As ToolStripSeparator
    Friend WithEvents BindingNavigatorMoveNextItem As ToolStripButton
    Friend WithEvents BindingNavigatorMoveLastItem As ToolStripButton
    Friend WithEvents BindingNavigatorSeparator2 As ToolStripSeparator
    Friend WithEvents PhonebookTableBindingNavigatorSaveItem As ToolStripButton
    Friend WithEvents First_NameTextBox As TextBox
    Friend WithEvents Last_NameTextBox As TextBox
    Friend WithEvents Phone_NumberTextBox As TextBox
    Friend WithEvents Email_AddressTextBox As TextBox
    Friend WithEvents Home_AddressTextBox As TextBox
    Friend WithEvents Button1 As Button
    Friend WithEvents Button2 As Button
    Friend WithEvents Button3 As Button
    Friend WithEvents Button4 As Button
    Friend WithEvents Button5 As Button
    Friend WithEvents Panel1 As Panel
    Friend WithEvents Button6 As Button
    Friend WithEvents DataGridView1 As DataGridView
    Friend WithEvents FirstNameDataGridViewTextBoxColumn As DataGridViewTextBoxColumn
    Friend WithEvents LastNameDataGridViewTextBoxColumn As DataGridViewTextBoxColumn
    Friend WithEvents PhoneNumberDataGridViewTextBoxColumn As DataGridViewTextBoxColumn
    Friend WithEvents EmailAddressDataGridViewTextBoxColumn As DataGridViewTextBoxColumn
    Friend WithEvents HomeAddressDataGridViewTextBoxColumn As DataGridViewTextBoxColumn
    Friend WithEvents PhonebookTableBindingSource1 As BindingSource
    Friend WithEvents PhonebookDataSet1BindingSource As BindingSource
End Class
