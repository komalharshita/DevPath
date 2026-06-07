import java.util.*;

class Book {
    String title;

    Book(String title) {
        this.title = title;
    }
}

public class LibraryManagement {
    public static void main(String[] args) {
        ArrayList<Book> books = new ArrayList<>();

        books.add(new Book("Java Basics"));
        books.add(new Book("Data Structures"));

        for (Book b : books) {
            System.out.println(b.title);
        }
    }
}