namespace OrderFixture;

public class PaymentFailedException : Exception
{
    public PaymentFailedException(string message)
        : base(message)
    {
    }

    public PaymentFailedException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
