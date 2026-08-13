namespace OrderFixture;

public interface IPaymentGateway
{
    /// <summary>Charges the customer. Returns true when the payment is approved.</summary>
    /// <exception cref="TimeoutException">Thrown when the payment provider does not respond in time.</exception>
    bool Charge(string customerId, decimal amount);
}
