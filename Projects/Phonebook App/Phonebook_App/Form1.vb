Public Class Form1

    Private Sub PhonebookTableBindingNavigatorSaveItem_Click(sender As Object, e As EventArgs) Handles PhonebookTableBindingNavigatorSaveItem.Click
        Me.Validate()
        Me.PhonebookTableBindingSource.EndEdit()
        Me.TableAdapterManager.UpdateAll(Me.PhonebookDataSet1)

    End Sub

    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        'TODO: This line of code loads data into the 'PhonebookDataSet1.PhonebookTable' table. You can move, or remove it, as needed.
        Me.PhonebookTableTableAdapter.Fill(Me.PhonebookDataSet1.PhonebookTable)
        DataGridView1.DataSource = PhonebookDataSet1.PhonebookTable
    End Sub

    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        Try
            Me.Validate()
            Me.PhonebookTableBindingSource.EndEdit()
            Me.TableAdapterManager.UpdateAll(Me.PhonebookDataSet1)
            MessageBox.Show("Contact Saved")
            PhonebookTableBindingSource.AddNew()
            First_NameTextBox.Select()
        Catch ex As Exception
            MessageBox.Show(ex.Message)
        End Try
    End Sub

    Private Sub Button4_Click(sender As Object, e As EventArgs) Handles Button4.Click
        Select Case MsgBox("Proceed to delete?", MsgBoxStyle.YesNo)
            Case MsgBoxResult.Yes
                Try
                    PhonebookTableBindingSource.RemoveCurrent()
                Catch ex As Exception
                    MessageBox.Show(ex.Message)
                End Try
            Case MsgBoxResult.No
                'Nothing
        End Select
    End Sub

    Private Sub Button5_Click(sender As Object, e As EventArgs) Handles Button5.Click
        Try
            PhonebookTableBindingSource.AddNew()
            First_NameTextBox.Select()
        Catch ex As Exception
            MessageBox.Show(ex.Message)
        End Try
    End Sub

    Private Sub Button2_Click(sender As Object, e As EventArgs) Handles Button2.Click
        Try
            PhonebookTableBindingSource.MovePrevious()
        Catch ex As Exception
            MessageBox.Show(ex.Message)
        End Try
    End Sub

    Private Sub Button3_Click(sender As Object, e As EventArgs) Handles Button3.Click
        Try
            PhonebookTableBindingSource.MoveNext()
        Catch ex As Exception
            MessageBox.Show(ex.Message)
        End Try
    End Sub

    Private Sub Button6_Click(sender As Object, e As EventArgs) Handles Button6.Click
        Try
            Me.Close()
        Catch ex As Exception
            MessageBox.Show(ex.Message)
        End Try
    End Sub
End Class
